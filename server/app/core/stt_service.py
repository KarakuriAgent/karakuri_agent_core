# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from faster_whisper import WhisperModel
from app.schemas.agent import AgentConfig
import numpy as np
import soundfile as sf
import io

class STTService:
    def __init__(self):
        self.model = WhisperModel("tiny", device="cpu", compute_type="int8")

    async def transcribe_audio(self, audio_content: bytes, agent_config: AgentConfig) -> str:
        try:
            audio_data, sample_rate = sf.read(io.BytesIO(audio_content))
            
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)

            segments, _ = self.model.transcribe(
                audio_data,
                beam_size=5,
                word_timestamps=False
            )

            text = " ".join([segment.text for segment in segments])
            
            return text.strip()

        except Exception as e:
            raise Exception(f"Failed to transcribe audio: {str(e)}")
