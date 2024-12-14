# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from app.dependencies import get_llm_service, get_tts_service, get_stt_service
from app.auth.api_key import get_api_key
from app.core.llm_service import LLMService
from app.core.tts_service import TTSService
from app.core.stt_service import STTService
from app.core.agent_manager import get_agent_manager
from app.utils.audio import calculate_audio_duration
import logging
from starlette.responses import FileResponse
from pathlib import Path
import os
import uuid
from typing import List
from app.core.config import get_settings
from app.schemas.chat import TextChatRequest, TextChatResponse, VoiceChatResponse

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()
UPLOAD_DIR = settings.chat_audio_files_dir
MAX_FILES = settings.chat_max_audio_files

@router.post("/text/text")
async def chat_text_to_text(
    request_body: TextChatRequest,
    api_key: str = Depends(get_api_key),
    llm_service: LLMService = Depends(get_llm_service),
):
    agent_id = request_body.agent_id
    message = request_body.message

    agent_manager = get_agent_manager()
    agent_config = agent_manager.get_agent(agent_id)
    
    if not agent_config:
        raise HTTPException(
            status_code=404,
            detail=f"Agent ID {agent_id} not found"
        )
    try:
        llm_response = await llm_service.generate_response(
            "text_to_text",
            message, 
            agent_config
        )
        return TextChatResponse(user_message=llm_response.user_message, 
                                agent_message=llm_response.agent_message,
                                  emotion=llm_response.emotion
                                  )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@router.post("/text/voice")
async def chat_text_to_voice(
    request: Request,
    request_body: TextChatRequest,
    api_key: str = Depends(get_api_key),
    llm_service: LLMService = Depends(get_llm_service),
    tts_service: TTSService = Depends(get_tts_service)
):
    agent_id = request_body.agent_id
    message = request_body.message

    agent_manager = get_agent_manager()
    agent_config = agent_manager.get_agent(agent_id)
    
    if not agent_config:
        raise HTTPException(
            status_code=404,
            detail=f"Agent ID {agent_id} not found"
        )

    try:
        llm_response = await llm_service.generate_response(
            "text_to_voice",
            message, 
            agent_config
        )

        audio_data = await tts_service.generate_speech(
            llm_response.agent_message, 
            agent_config
        )

        scheme = request.headers.get('X-Forwarded-Proto', 'http')
        server_host = request.headers.get('X-Forwarded-Host', request.base_url.hostname)
        base_url = f"{scheme}://{server_host}"
        
        audio_url = await upload_to_storage(base_url, audio_data)

        duration = calculate_audio_duration(audio_data)
        return VoiceChatResponse(user_message=message, 
                                 agent_message=llm_response.agent_message, 
                                 emotion=llm_response.emotion,
                                 audio_url=audio_url, 
                                 duration=duration
                                 )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@router.post("/voice/text")
async def chat_voice_to_text(
    agent_id: str,
    audio_file: UploadFile = File(...),
    api_key: str = Depends(get_api_key),
    llm_service: LLMService = Depends(get_llm_service),
    stt_service: STTService = Depends(get_stt_service)
):
    agent_manager = get_agent_manager()
    agent_config = agent_manager.get_agent(agent_id)
    
    if not agent_config:
        raise HTTPException(
            status_code=404,
            detail=f"Agent ID {agent_id} not found"
        )

    try:
        audio_content = await audio_file.read()
        
        text_message = await stt_service.transcribe_audio(
            audio_content,
            agent_config
        )

        llm_response = await llm_service.generate_response(
            "voice_to_text",
            text_message, 
            agent_config
        )

        return TextChatResponse(user_message=llm_response.user_message, 
                                agent_message=llm_response.agent_message,
                                  emotion=llm_response.emotion
                                  )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@router.post("/voice/voice")
async def chat_voice_to_voice(
    request: Request,
    agent_id: str,
    audio_file: UploadFile = File(...),
    api_key: str = Depends(get_api_key),
    llm_service: LLMService = Depends(get_llm_service),
    stt_service: STTService = Depends(get_stt_service),
    tts_service: TTSService = Depends(get_tts_service)
):
    agent_manager = get_agent_manager()
    agent_config = agent_manager.get_agent(agent_id)
    
    if not agent_config:
        raise HTTPException(
            status_code=404,
            detail=f"Agent ID {agent_id} not found"
        )

    try:
        audio_content = await audio_file.read()
        
        text_message = await stt_service.transcribe_audio(
            audio_content,
            agent_config
        )

        llm_response = await llm_service.generate_response(
            "voice_to_voice",
            text_message, 
            agent_config
        )

        audio_data = await tts_service.generate_speech(
            llm_response.agent_message, 
            agent_config
        )

        scheme = request.headers.get('X-Forwarded-Proto', 'http')
        server_host = request.headers.get('X-Forwarded-Host', request.base_url.hostname)
        base_url = f"{scheme}://{server_host}"
        
        audio_url = await upload_to_storage(base_url, audio_data)
        duration = calculate_audio_duration(audio_data)

        return VoiceChatResponse(user_message=text_message, 
                                 agent_message=llm_response.agent_message, 
                                 emotion=llm_response.emotion,
                                 audio_url=audio_url, 
                                 duration=duration
                                 )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

async def upload_to_storage(base_url: str, audio_data: bytes) -> str:
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.wav")

    await cleanup_old_files(UPLOAD_DIR)

    with open(file_path, "wb") as f:
        f.write(audio_data)
    return f"{base_url}/v1/chat/{UPLOAD_DIR}/{file_id}"

async def cleanup_old_files(directory: str):
    files = Path(directory).glob('*.wav')
    files_with_time: List[tuple[float, Path]] = [
        (f.stat().st_ctime, f) for f in files if f.is_file()
    ]
    files_with_time.sort()
    if len(files_with_time) >= MAX_FILES:
        files_to_delete = files_with_time[:(len(files_with_time) - MAX_FILES + 1)]
        for _, file_path in files_to_delete:
            try:
                file_path.unlink() 
            except Exception as e:
                logger.error(f"Error deleting file {file_path}: {e}")

@router.get(f"/{UPLOAD_DIR}/{{file_name}}")
async def get_audio(file_name: str):
    file_path = Path(f"{UPLOAD_DIR}/{file_name}.wav")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path)
