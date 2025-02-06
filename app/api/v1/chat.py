# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, Request
from litellm import cast
from app.core.memory.memory_service import MemoryService
from app.dependencies import (
    get_llm_service,
    get_memory_service,
    get_tts_service,
    get_stt_service,
)
from app.auth.api_key import verify_token
from app.core.llm_service import LLMService
from app.core.tts_service import TTSService
from app.core.stt_service import STTService
from app.core.agent_manager import AgentManager, get_agent_manager
from app.schemas.llm import LLMResponse
from app.utils.audio import calculate_audio_duration, upload_to_storage
import logging
from starlette.responses import FileResponse
from pathlib import Path
from typing import Optional
from app.core.config import get_settings
from app.schemas.chat import TextChatResponse, VoiceChatResponse

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()
UPLOAD_DIR = settings.chat_audio_files_dir
MAX_FILES = settings.chat_max_audio_files


@router.post("/text/text")
async def chat_text_to_text(
    agent_id: str = Form(...),
    user_id: str = Form(...),
    message: str = Form(...),
    image_file: Optional[UploadFile] = None,
    api_key: str = Depends(verify_token),
    llm_service: LLMService = Depends(get_llm_service),
    memory_service: MemoryService = Depends(get_memory_service),
    agent_manager: AgentManager = Depends(get_agent_manager),
):
    try:
        agent_config = agent_manager.get_agent(agent_id)
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Agent with ID '{agent_id}' not found."
        )

    user_config = await memory_service.get_user(agent_id, user_id)
    if user_config is None:
        raise HTTPException(
            status_code=404, detail=f"User with user_id '{user_id}' not found."
        )

    if image_file is not None:
        image_content = await image_file.read()
    else:
        image_content = None

    try:
        llm_response = cast(
            LLMResponse,
            await llm_service.generate_response(
                message_type="talk",
                message=message,
                agent_config=agent_config,
                user_config=user_config,
                image=image_content,
            ),
        )
        return TextChatResponse(
            user_message=llm_response.user_message,
            agent_message=llm_response.agent_message,
            emotion=llm_response.emotion,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


@router.post("/text/voice")
async def chat_text_to_voice(
    request: Request,
    agent_id: str = Form(...),
    user_id: str = Form(...),
    message: str = Form(...),
    image_file: Optional[UploadFile] = None,
    api_key: str = Depends(verify_token),
    llm_service: LLMService = Depends(get_llm_service),
    tts_service: TTSService = Depends(get_tts_service),
    memory_service: MemoryService = Depends(get_memory_service),
    agent_manager: AgentManager = Depends(get_agent_manager),
):
    try:
        agent_config = agent_manager.get_agent(agent_id)
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Agent with ID '{agent_id}' not found."
        )

    user_config = await memory_service.get_user(agent_id, user_id)
    if user_config is None:
        raise HTTPException(
            status_code=404, detail=f"User with user_id '{user_id}' not found."
        )

    if image_file is not None:
        image_content = await image_file.read()
    else:
        image_content = None

    try:
        llm_response = cast(
            LLMResponse,
            await llm_service.generate_response(
                message_type="talk",
                message=message,
                agent_config=agent_config,
                user_config=user_config,
                image=image_content,
            ),
        )

        audio_data = await tts_service.generate_speech(
            llm_response.agent_message, agent_config
        )

        scheme = request.headers.get("X-Forwarded-Proto", "http")
        server_host = request.headers.get("X-Forwarded-Host", request.base_url.hostname)
        base_url = f"{scheme}://{server_host}"

        audio_url = await upload_to_storage(
            base_url, audio_data, "chat", UPLOAD_DIR, MAX_FILES
        )

        duration = calculate_audio_duration(audio_data)
        return VoiceChatResponse(
            user_message=message,
            agent_message=llm_response.agent_message,
            emotion=llm_response.emotion,
            audio_url=audio_url,
            duration=duration,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


@router.post("/voice/text")
async def chat_voice_to_text(
    agent_id: str = Form(...),
    user_id: str = Form(...),
    image_file: Optional[UploadFile] = None,
    audio_file: UploadFile = File(...),
    api_key: str = Depends(verify_token),
    llm_service: LLMService = Depends(get_llm_service),
    stt_service: STTService = Depends(get_stt_service),
    memory_service: MemoryService = Depends(get_memory_service),
    agent_manager: AgentManager = Depends(get_agent_manager),
):
    try:
        agent_config = agent_manager.get_agent(agent_id)
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Agent with ID '{agent_id}' not found."
        )

    user_config = await memory_service.get_user(agent_id, user_id)
    if user_config is None:
        raise HTTPException(
            status_code=404, detail=f"User with user_id '{user_id}' not found."
        )

    if image_file is not None:
        image_content = await image_file.read()
    else:
        image_content = None

    try:
        audio_content = await audio_file.read()

        text_message = await stt_service.transcribe_audio(audio_content, agent_config)

        llm_response = cast(
            LLMResponse,
            await llm_service.generate_response(
                message_type="talk",
                message=text_message,
                agent_config=agent_config,
                user_config=user_config,
                image=image_content,
            ),
        )

        return TextChatResponse(
            user_message=llm_response.user_message,
            agent_message=llm_response.agent_message,
            emotion=llm_response.emotion,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


@router.post("/voice/voice")
async def chat_voice_to_voice(
    request: Request,
    agent_id: str = Form(...),
    user_id: str = Form(...),
    image_file: Optional[UploadFile] = None,
    audio_file: UploadFile = File(...),
    api_key: str = Depends(verify_token),
    llm_service: LLMService = Depends(get_llm_service),
    stt_service: STTService = Depends(get_stt_service),
    tts_service: TTSService = Depends(get_tts_service),
    memory_service: MemoryService = Depends(get_memory_service),
    agent_manager: AgentManager = Depends(get_agent_manager),
):
    try:
        agent_config = agent_manager.get_agent(agent_id)
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Agent with ID '{agent_id}' not found."
        )

    user_config = await memory_service.get_user(agent_id, user_id)
    if user_config is None:
        raise HTTPException(
            status_code=404, detail=f"User with user_id '{user_id}' not found."
        )

    if image_file is not None:
        image_content = await image_file.read()
    else:
        image_content = None

    try:
        audio_content = await audio_file.read()

        text_message = await stt_service.transcribe_audio(audio_content, agent_config)

        llm_response = cast(
            LLMResponse,
            await llm_service.generate_response(
                message_type="talk",
                message=text_message,
                agent_config=agent_config,
                user_config=user_config,
                image=image_content,
            ),
        )

        audio_data = await tts_service.generate_speech(
            llm_response.agent_message, agent_config
        )

        scheme = request.headers.get("X-Forwarded-Proto", "http")
        server_host = request.headers.get("X-Forwarded-Host", request.base_url.hostname)
        base_url = f"{scheme}://{server_host}"

        audio_url = await upload_to_storage(
            base_url, audio_data, "chat", UPLOAD_DIR, MAX_FILES
        )
        duration = calculate_audio_duration(audio_data)

        return VoiceChatResponse(
            user_message=text_message,
            agent_message=llm_response.agent_message,
            emotion=llm_response.emotion,
            audio_url=audio_url,
            duration=duration,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


@router.get(f"/{UPLOAD_DIR}/{{file_name}}")
async def get_audio(file_name: str):
    if ".." in file_name or "/" in file_name:
        raise HTTPException(status_code=400, detail="Invalid file name")
    file_path = Path(f"{UPLOAD_DIR}/{file_name}.wav")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path)
