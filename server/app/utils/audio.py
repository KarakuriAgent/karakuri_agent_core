from pydub import AudioSegment
import io
import logging

logger = logging.getLogger(__name__)

def calculate_audio_duration(audio_data: bytes) -> int:
    try:
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="wav")
        return len(audio_segment)
    except Exception as e:
        logger.error(f"Error calculating audio duration: {e}")
        return 0