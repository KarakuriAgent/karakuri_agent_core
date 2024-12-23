# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.responses import FileResponse
from app.core.llm_service import LLMService
from app.core.tts_service import TTSService
from app.core.stt_service import STTService
from app.dependencies import get_llm_service, get_stt_service, get_tts_service
from app.utils.audio import calculate_audio_duration
from pathlib import Path
import os
import uuid
from typing import Dict, List, cast
from app.core.agent_manager import get_agent_manager
from app.core.config import get_settings
import logging
from linebot import AsyncLineBotApi # type: ignore
from linebot.aiohttp_async_http_client import AiohttpAsyncHttpClient # type: ignore
from linebot.v3.messaging.async_api_client import AsyncApiClient # type: ignore
from linebot.v3.messaging import AsyncMessagingApi # type: ignore
from linebot.v3.webhook import WebhookParser # type: ignore
from linebot.v3.webhooks.models import Event # type: ignore
from linebot.v3.messaging.models import ( # type: ignore
    ReplyMessageRequest,
    TextMessage,
    AudioMessage
)
from linebot.v3.exceptions import ( # type: ignore
    InvalidSignatureError
)
from linebot.v3.webhooks import ( # type: ignore
    MessageEvent,
    TextMessageContent,
    ImageMessageContent,
    Configuration
)

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()
UPLOAD_DIR = settings.line_audio_files_dir
MAX_FILES = settings.line_max_audio_files
user_image_cache: Dict[str, bytes] = {}

@router.post("/callback/{agent_id}")
async def handle_line_callback(
    request: Request,
    agent_id: str,
    llm_service: LLMService = Depends(get_llm_service),
    tts_service: TTSService = Depends(get_tts_service),
    stt_service: STTService = Depends(get_stt_service)
):
    signature, body = await extract_line_request_data(request)
    agent_manager = get_agent_manager()
    try:
        agent_config = agent_manager.get_agent(agent_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Agent with ID '{agent_id}' not found.")
    aio_session = aiohttp.ClientSession()
    async_client: AsyncApiClient | None = None
    try:
        configuration = Configuration(
            access_token=agent_config.line_channel_access_token
         )
        async_client = AsyncApiClient(configuration)
        line_messaging_api = AsyncMessagingApi(async_client)
        
        aio_client = AiohttpAsyncHttpClient(aio_session)
        line_bot_api = AsyncLineBotApi(
            channel_access_token=agent_config.line_channel_access_token,
            async_http_client=aio_client
        )

        events = parse_line_events(body, signature, agent_config.line_channel_secret)
        try:
            for event in events:
                if not isinstance(event, MessageEvent):
                    continue

                if isinstance(event.message, ImageMessageContent):
                    await process_image_message(line_bot_api)
                    continue
                elif isinstance(event.message, TextMessageContent):
                    text_message = event.message.text
                else:
                    continue
                cached_image_bytes = user_image_cache.pop(event.source.user_id, None) # type: ignore
                llm_response = await llm_service.generate_response(
                    "line",
                    text_message,
                    agent_config,
                    image=cached_image_bytes
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

                await line_messaging_api.reply_message( # type: ignore
                    ReplyMessageRequest(
                        reply_token=event.reply_token, # type: ignore
                        messages=[
                            TextMessage(text=llm_response.agent_message), # type: ignore
                            AudioMessage(original_content_url=audio_url, duration=duration) # type: ignore
                        ]
                    )
                )

            return 'OK'

        except Exception as e:
            logger.exception("Error in handle_line_callback:", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error processing request: {str(e)}"
            )
    finally:
        await aio_session.close()
        if async_client is not None:
            await async_client.close()

async def extract_line_request_data(request: Request):
    signature = request.headers['X-Line-Signature']
    body = await request.body()
    return signature, body.decode()

def parse_line_events(body: str, signature: str, line_channel_secret: str) -> List[Event]:
    line_parser = WebhookParser(line_channel_secret)

    try:
        events: List[Event] = cast(List[Event], line_parser.parse(body, signature))  # type: ignore
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return events

async def process_image_message(line_bot_api: AsyncLineBotApi):
    message_content = await line_bot_api.get_message_content(event.message.id) # type: ignore
    image_bytes: bytes = b''
        async for chunk in message_content.iter_content(): # type: ignore
            assert isinstance(chunk, bytes)  
            image_bytes += chunk
        user_image_cache[event.source.user_id] = image_bytes # type: ignore

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
@router.get(f"/{UPLOAD_DIR}/{{file_name}}")
async def get_audio(file_name: str):
    if '..' in file_name or '/' in file_name:
        raise HTTPException(status_code=400, detail="Invalid file name")
    file_path = Path(f"{UPLOAD_DIR}/{file_name}.wav")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path)
