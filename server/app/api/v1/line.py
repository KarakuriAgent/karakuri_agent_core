# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.responses import FileResponse
from app.dependencies import get_llm_service, get_tts_service
from app.utils.audio import calculate_audio_duration
from pathlib import Path
from pydub import AudioSegment
import io
import os
import uuid
from typing import List
from app.core.agent_manager import get_agent_manager
from app.core.config import get_settings
import logging
from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    ReplyMessageRequest,
    TextMessage,
    AudioMessage
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()
UPLOAD_DIR = settings.line_audio_files_dir
MAX_FILES = settings.line_max_audio_files

@router.post("/callback/{agent_id}")
async def handle_line_callback(
    request: Request,
    agent_id: str, 
    llm_service = Depends(get_llm_service),
    tts_service = Depends(get_tts_service)
):
    signature = request.headers['X-Line-Signature']

    body = await request.body()
    body = body.decode()

    agent_manager = get_agent_manager()
    try:
        agent_config = agent_manager.get_agent(agent_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Agent with ID '{agent_id}' not found.")
    
    configuration = Configuration(
        access_token=agent_config.line_channel_access_token
    )
    line_async_api_client = AsyncApiClient(configuration)
    line_bot_api = AsyncMessagingApi(line_async_api_client)
    line_parser = WebhookParser(agent_config.line_channel_secret)

    try:
        events = line_parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    try:
        for event in events:
            if not isinstance(event, MessageEvent):
                continue
            if not isinstance(event.message, TextMessageContent):
                continue

            llm_response = await llm_service.generate_response(
                "line",
                event.message.text, 
                agent_config
            )
            message = llm_response["agent_message"].rstrip('\n')

            audio_data = await tts_service.generate_speech(
                message, 
                agent_config
            )

            scheme = request.headers.get('X-Forwarded-Proto', 'http')
            server_host = request.headers.get('X-Forwarded-Host', request.base_url.hostname)
            base_url = f"{scheme}://{server_host}"

            audio_url = await upload_to_storage(base_url, audio_data)
            duration = calculate_audio_duration(audio_data)
            
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text=message),
                        AudioMessage(original_content_url=audio_url, duration=duration)
                    ]
                )
            )
            
        await line_async_api_client.close()
        return 'OK'
        
    except Exception as e:
        await line_async_api_client.close()
        logger.exception("Error in handle_line_callback:", exc_info=True)
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
    return f"{base_url}/v1/line/{UPLOAD_DIR}/{file_id}"

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
