from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File, Request
from starlette.responses import FileResponse
from pathlib import Path
import io
import os
import uuid
import wave
from typing import List
from app.auth.api_key import get_api_key
from app.core.agent_manager import get_agent_manager
from app.core.llm_service import LLMService
from app.core.tts_service import TTSService
from app.schemas.agent import AgentResponse
from app.core.stt_service import STTService
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
llm_service = LLMService()
stt_service = STTService()
tts_service = TTSService()
logger = logging.getLogger(__name__)
UPLOAD_DIR = "audio_files" 

@router.post("/line/callback/{agent_id}")
async def handle_line_callback(request: Request, agent_id: str):
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

        audio_data = await tts_service.generate_speech(
            llm_response, 
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
                messages=[TextMessage(text=llm_response),
                           AudioMessage(original_content_url=audio_url, duration=duration)]
                )
            )
        return 'OK'
    except Exception as e:
        logger.exception("Error in handle_line_callback:", exc_info=True)
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
    return f"{base_url}/v1/{UPLOAD_DIR}/{file_id}"

async def cleanup_old_files(directory: str):
    settings = get_settings()
    max_files = settings.line_max_audio_files
    files = Path(directory).glob('*.wav')
    files_with_time: List[tuple[float, Path]] = [
        (f.stat().st_ctime, f) for f in files if f.is_file()
    ]
    files_with_time.sort()
    if len(files_with_time) >= max_files:
        files_to_delete = files_with_time[:(len(files_with_time) - max_files + 1)]
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

@router.post("/chat/text/text")
async def chat_text_to_text(agent_id: str, message: str, api_key: str = Depends(get_api_key)):
    """
    チャットエンドポイント
    音声データ（WAV形式）を返します
    """
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

        return Response(content=llm_response)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@router.post("/chat/text/voice")
async def chat_text_to_voice(agent_id: str, message: str, api_key: str = Depends(get_api_key)):
    """
    チャットエンドポイント
    音声データ（WAV形式）を返します
    """
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
            llm_response, 
            agent_config
        )

        return Response(
            content=audio_data,
            media_type="audio/wav"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@router.post("/chat/voice/text")
async def chat_voice_to_text(
    agent_id: str,
    audio_file: UploadFile = File(...),
    api_key: str = Depends(get_api_key)):
    """
    チャットエンドポイント
    音声データ（WAV形式）を返します
    """
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

        return Response(content=llm_response)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@router.post("/chat/voice/voice")
async def chat_voice_to_voice(
    agent_id: str,
    audio_file: UploadFile = File(...),
    api_key: str = Depends(get_api_key)):
    """
    チャットエンドポイント
    音声データ（WAV形式）を返します
    """
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
            llm_response, 
            agent_config
        )

        return Response(
            content=audio_data,
            media_type="audio/wav"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@router.get("/agents")
async def list_agents(api_key: str = Depends(get_api_key)):
    """
    登録されているエージェントの一覧を返します
    """
    try:
        agent_manager = get_agent_manager()
        agents = agent_manager.get_all_agents()
        return [
            AgentResponse(agent_id=id, agent_name=name)
            for id, name in agents
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching agents: {str(e)}"
        )
