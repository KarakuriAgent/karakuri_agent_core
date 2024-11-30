from faster_whisper import WhisperModel
from app.schemas.agent import AgentConfig
import numpy as np
import soundfile as sf
import io

class STTService:
    def __init__(self):
        # モデルの初期化
        # model_size_or_path can be "tiny", "base", "small", "medium", "large-v1", "large-v2", "large-v3"
        # GPU使用の場合は以下のように設定
        # self.model = WhisperModel("medium", device="cuda", compute_type="float16")
        # CPU使用の場合は以下のように設定
        self.model = WhisperModel("tiny", device="cpu", compute_type="int8")

    async def transcribe_audio(self, audio_content: bytes, agent_config: AgentConfig) -> str:
        """
        音声データをテキストに変換します
        
        Args:
            audio_content (bytes): WAV形式の音声データ
            agent_config (AgentConfig): エージェントの設定
            
        Returns:
            str: 変換されたテキスト
        """
        try:
            audio_data, sample_rate = sf.read(io.BytesIO(audio_content))
            
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)

            segments, _ = self.model.transcribe(
                audio_data,
                ## language="ja",
                beam_size=5,
                word_timestamps=False
            )

            text = " ".join([segment.text for segment in segments])
            
            return text.strip()

        except Exception as e:
            raise Exception(f"Failed to transcribe audio: {str(e)}")
