# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
import aiohttp
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from starlette.requests import ClientDisconnect
from starlette.responses import FileResponse
from app.core.llm_service import LLMService
from app.core.schedule_service import ScheduleService
from app.core.tts_service import TTSService
from app.core.stt_service import STTService
from app.dependencies import (
    get_llm_service,
    get_schedule_service,
    get_stt_service,
    get_tts_service,
)
from app.schemas.status import CommunicationChannel
from app.utils.audio import calculate_audio_duration, upload_to_storage
from pathlib import Path
from typing import Dict, cast, List
from app.schemas.agent import AgentConfig
from app.core.agent_manager import get_agent_manager
from app.core.config import get_settings
import logging
from linebot import AsyncLineBotApi  # type: ignore
from linebot.aiohttp_async_http_client import AiohttpAsyncHttpClient  # type: ignore
from linebot.v3.messaging.async_api_client import AsyncApiClient  # type: ignore
from linebot.v3.messaging import AsyncMessagingApi  # type: ignore
from linebot.v3.webhook import WebhookParser  # type: ignore
from linebot.v3.webhooks.models import Event  # type: ignore
from linebot.v3.messaging.models import (  # type: ignore
    ReplyMessageRequest,
    TextMessage,
    AudioMessage,
)
from linebot.v3.exceptions import (  # type: ignore
    InvalidSignatureError,
)
from linebot.v3.webhooks import (  # type: ignore
    MessageEvent,
    TextMessageContent,
    ImageMessageContent,
    Configuration,
)

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()
UPLOAD_DIR = settings.line_audio_files_dir
MAX_FILES = settings.line_max_audio_files
user_image_cache: Dict[str, bytes] = {}


async def process_line_events_background(
    body: str,
    signature: str,
    agent_config: AgentConfig,
    request: Request,
    llm_service: LLMService,
    tts_service: TTSService,
    schedule_service: ScheduleService,
):
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
            async_http_client=aio_client,
        )

        events = parse_line_events(body, signature, agent_config.line_channel_secret)
        try:
            for event in events:
                if not isinstance(event, MessageEvent):
                    continue

                if isinstance(event.message, ImageMessageContent):
                    await process_image_message(line_bot_api, event)
                    continue
                elif isinstance(event.message, TextMessageContent):
                    text_message = event.message.text
                else:
                    continue
                cached_image_bytes = user_image_cache.pop(event.source.user_id, None)  # type: ignore
                status_context = schedule_service.get_current_status_context(
                    agent_config=agent_config,
                    communication_channel=CommunicationChannel.CHAT,
                )
                llm_response = await llm_service.generate_response(
                    text_message, agent_config, status_context, image=cached_image_bytes
                )
                audio_data = await tts_service.generate_speech(
                    llm_response.agent_message, agent_config
                )
                scheme = request.headers.get("X-Forwarded-Proto", "http")
                server_host = request.headers.get(
                    "X-Forwarded-Host", request.base_url.hostname
                )
                base_url = f"{scheme}://{server_host}"
                audio_url = await upload_to_storage(
                    base_url, audio_data, "line", UPLOAD_DIR, MAX_FILES
                )
                duration = calculate_audio_duration(audio_data)

                await line_messaging_api.reply_message(  # type: ignore
                    ReplyMessageRequest(
                        reply_token=event.reply_token,  # type: ignore
                        messages=[
                            TextMessage(text=llm_response.agent_message),  # type: ignore
                            AudioMessage(
                                original_content_url=audio_url,  # type: ignore
                                duration=duration,
                            ),
                        ],
                    )
                )
        except Exception as e:
            logger.exception(
                f"Error in process_line_events_background: {str(e)}", exc_info=True
            )
    finally:
        await aio_session.close()
        if async_client is not None:
            await async_client.close()


@router.post("/callback/{agent_id}")
async def handle_line_callback(
    background_tasks: BackgroundTasks,
    request: Request,
    agent_id: str,
    llm_service: LLMService = Depends(get_llm_service),
    tts_service: TTSService = Depends(get_tts_service),
    stt_service: STTService = Depends(get_stt_service),
    schedule_service: ScheduleService = Depends(get_schedule_service),
):
    signature, body = await extract_line_request_data(request)
    agent_manager = get_agent_manager()
    try:
        agent_config = agent_manager.get_agent(agent_id)
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Agent with ID '{agent_id}' not found."
        )

    # Verify signature before returning OK
    parse_line_events(body, signature, agent_config.line_channel_secret)

    background_tasks.add_task(
        process_line_events_background,
        body,
        signature,
        agent_config,
        request,
        llm_service,
        tts_service,
        schedule_service,
    )
    return "OK"


async def extract_line_request_data(request: Request):
    try:
        signature = request.headers.get("X-Line-Signature")
        if not signature:
            raise HTTPException(
                status_code=400, detail="X-Line-Signature header is missing"
            )

        body = await request.body()
        return signature, body.decode()
    except ClientDisconnect:
        logger.warning("Client disconnected while reading request body")
        raise HTTPException(status_code=400, detail="Client disconnected")
    except Exception as e:
        logger.error(f"Error extracting LINE request data: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid request")


def parse_line_events(
    body: str, signature: str, line_channel_secret: str
) -> List[Event]:
    line_parser = WebhookParser(line_channel_secret)

    try:
        events: List[Event] = cast(List[Event], line_parser.parse(body, signature))  # type: ignore
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return events


async def process_image_message(line_bot_api: AsyncLineBotApi, event: MessageEvent):
    message_content = await line_bot_api.get_message_content(event.message.id)  # type: ignore
    image_bytes: bytes = b""
    async for chunk in message_content.iter_content():  # type: ignore
        assert isinstance(chunk, bytes)
        image_bytes += chunk
    user_image_cache[event.source.user_id] = image_bytes  # type: ignore


@router.get(f"/{UPLOAD_DIR}/{{file_name}}")
async def get_audio(file_name: str):
    if ".." in file_name or "/" in file_name:
        raise HTTPException(status_code=400, detail="Invalid file name")
    file_path = Path(f"{UPLOAD_DIR}/{file_name}.wav")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path)
