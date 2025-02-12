# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import FileResponse
from pathlib import Path

from app.core.config import Settings, get_settings
from app.core.tts_service import TTSService
from app.core.stt_service import STTService
from app.core.agent_manager import AgentManager
from app.dependencies import (
    get_tts_service,
    get_stt_service,
    get_agent_manager,
)
from app.auth.api_key import verify_token
from app.schemas.audio import TextResponse, VoiceResponse
from app.utils.audio import calculate_audio_duration, get_base_url, upload_to_storage

router = APIRouter()

settings = get_settings()
UPLOAD_DIR = settings.talk_audio_files_dir


@router.post("/text-to-speech")
async def text_to_speech(
    request: Request,
    agent_id: str = Form(...),
    text: str = Form(...),
    api_key: str = Depends(verify_token),
    tts_service: TTSService = Depends(get_tts_service),
    agent_manager: AgentManager = Depends(get_agent_manager),
    settings: Settings = Depends(get_settings),
) -> VoiceResponse:
    agent_config = agent_manager.get_agent(agent_id)
    audio_data = await tts_service.generate_speech(text, agent_config)
    base_url = get_base_url(request)
    audio_url = await upload_to_storage(
        base_url,
        audio_data,
        "utils/audio",
        settings.talk_audio_files_dir,
        settings.talk_max_audio_files,
    )
    duration = calculate_audio_duration(audio_data)
    return VoiceResponse(audio_url=audio_url, duration=duration)


@router.post("/speech-to-text")
async def speech_to_text(
    audio_file: UploadFile = File(...),
    api_key: str = Depends(verify_token),
    stt_service: STTService = Depends(get_stt_service),
) -> TextResponse:
    audio_content = await audio_file.read()
    text = await stt_service.transcribe_audio(audio_content)
    return TextResponse(text=text)


@router.get(f"/{UPLOAD_DIR}/{{file_name}}")
async def get_audio(file_name: str):
    if ".." in file_name or "/" in file_name:
        raise HTTPException(status_code=400, detail="Invalid file name")
    file_path = Path(f"{UPLOAD_DIR}/{file_name}.wav")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path)
