import os
from pydub import AudioSegment  # type: ignore
import io
from typing import List
import uuid
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


async def upload_to_storage(
    base_url: str, audio_data: bytes, type: str, upload_dir: str, max_files: int
) -> str:
    Path(upload_dir).mkdir(parents=True, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(upload_dir, f"{file_id}.wav")

    await cleanup_old_files(upload_dir, max_files)

    with open(file_path, "wb") as f:
        f.write(audio_data)
    return f"{base_url}/v1/{type}/{upload_dir}/{file_id}"


async def cleanup_old_files(directory: str, max_files: int):
    files = Path(directory).glob("*.wav")
    files_with_time: List[tuple[float, Path]] = [
        (f.stat().st_ctime, f) for f in files if f.is_file()
    ]
    files_with_time.sort()
    if len(files_with_time) >= max_files:
        files_to_delete = files_with_time[: (len(files_with_time) - max_files)]
        for _, file_path in files_to_delete:
            try:
                file_path.unlink()
            except Exception as e:
                logger.error(f"Error deleting file {file_path}: {e}")


def calculate_audio_duration(audio_data: bytes) -> int:
    try:
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="wav")  # type: ignore
        return len(audio_segment)  # type: ignore
    except Exception as e:
        logger.error(f"Error calculating audio duration: {e}")
        return 0
