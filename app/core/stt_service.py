# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from faster_whisper import WhisperModel
from app.schemas.agent import AgentConfig
import soundfile as sf
import io


class STTService:
    def __init__(self):
        self.model = WhisperModel("tiny", device="cpu", compute_type="int8")

    async def process_voice_stream(self, audio_stream: bytes, agent_config: AgentConfig) -> Optional[str]:
        try:
            # VAD処理
            speech_segments = self.vad_process(audio_stream)
            if not speech_segments:
                return None

            # 音声認識（STT）処理
            text_results = []
            for segment in speech_segments:
                text = await self.transcribe_audio(segment, agent_config)
                if text:
                    text_results.append(text)

            return " ".join(text_results) if text_results else None

        except Exception as e:
            logger.error(f"Error processing voice stream: {str(e)}")
            raise

    def vad_process(self, audio_data: bytes) -> List[bytes]:
        import webrtcvad
        import numpy as np

        # VADの設定
        vad = webrtcvad.Vad()
        vad.set_mode(3)  # 最も厳しいモード

        # 音声データのパラメータ
        sample_rate = 16000  # 16kHz
        frame_duration = 30  # 30ms
        frame_size = int(sample_rate * frame_duration / 1000)

        # 音声データをフレームに分割
        frames = [audio_data[i:i + frame_size] for i in range(0, len(audio_data), frame_size)]

        # 発話部分を抽出
        speech_frames = []
        for frame in frames:
            if len(frame) < frame_size:
                continue  # 最後の不完全なフレームは無視
            if vad.is_speech(frame, sample_rate):
                speech_frames.append(frame)

        # 発話部分を結合して返す
        return speech_frames

    async def transcribe_audio(self, audio_content: bytes, agent_config: AgentConfig) -> str:
        try:
            audio_data, sample_rate = sf.read(io.BytesIO(audio_content))

            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)

            segments, _ = self.model.transcribe(
                audio_data, beam_size=5, word_timestamps=False
            )

            text = " ".join([segment.text for segment in segments])

            return text.strip()

        except Exception as e:
            logger.error(f"Failed to transcribe audio: {str(e)}")
            raise
