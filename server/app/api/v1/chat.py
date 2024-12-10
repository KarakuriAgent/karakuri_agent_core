# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File, Request
from app.dependencies import get_llm_service, get_tts_service, get_stt_service
from app.auth.api_key import get_api_key
from app.core.agent_manager import get_agent_manager
import logging
import json
from starlette.responses import FileResponse
from pathlib import Path
import io
import os
import uuid
import wave
from typing import List
from app.core.config import get_settings
from app.schemas.chat import TextChatRequest

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()
UPLOAD_DIR = settings.chat_audio_files_dir
MAX_FILES = settings.chat_max_audio_files

@router.post("/text/text")
async def chat_text_to_text(
    request_body: TextChatRequest,
    api_key: str = Depends(get_api_key),
    llm_service = Depends(get_llm_service),
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
        return Response(content=json.dumps(llm_response, ensure_ascii=False))
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
    llm_service = Depends(get_llm_service),
    tts_service = Depends(get_tts_service)
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
        agent_message = llm_response["agent_message"].rstrip('\n')
        emotion = llm_response["emotion"]

        audio_data = await tts_service.generate_speech(
            agent_message, 
            agent_config
        )

        scheme = request.headers.get('X-Forwarded-Proto', 'http')
        server_host = request.headers.get('X-Forwarded-Host', request.base_url.hostname)
        base_url = f"{scheme}://{server_host}"
        
        audio_url = await upload_to_storage(base_url, audio_data)
        duration = calculate_audio_duration(audio_data)
        return Response(content=json.dumps({
            "audio_url": audio_url,
            "duration": duration,
            "user_message": message,
            "agent_message": agent_message,
            "emotion": emotion,
        }, ensure_ascii=False))
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
    llm_service = Depends(get_llm_service),
    stt_service = Depends(get_stt_service)
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

        return Response(content=json.dumps(llm_response, ensure_ascii=False))
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
    llm_service = Depends(get_llm_service),
    stt_service = Depends(get_stt_service),
    tts_service = Depends(get_tts_service)
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
        agent_message = llm_response["agent_message"].rstrip('\n')
        emotion = llm_response["emotion"]

        audio_data = await tts_service.generate_speech(
            agent_message, 
            agent_config
        )


        scheme = request.headers.get('X-Forwarded-Proto', 'http')
        server_host = request.headers.get('X-Forwarded-Host', request.base_url.hostname)
        base_url = f"{scheme}://{server_host}"
        
        audio_url = await upload_to_storage(base_url, audio_data)
        duration = calculate_audio_duration(audio_data)
        return Response(content=json.dumps({
            "audio_url": audio_url,
            "duration": duration,
            "user_message": text_message,
            "agent_message": agent_message,
            "emotion": emotion,
        }, ensure_ascii=False))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

def calculate_audio_duration(audio_data: bytes) -> int:
    with io.BytesIO(audio_data) as audio_io:
        with wave.open(audio_io, 'rb') as wav:
            frames = wav.getnframes()
            rate = wav.getframerate()
            duration = int((frames / rate) * 1000)
            return duration

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

@router.get(f"/{UPLOAD_DIR}/{{file_path}}")
async def get_audio(file_path: str):
    file_path = Path(f"{UPLOAD_DIR}/{file_path}.wav")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path)
