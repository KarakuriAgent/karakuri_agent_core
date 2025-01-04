from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends, Query
from app.core.stt_service import STTService
from app.core.llm_service import LLMService
from app.core.tts_service import TTSService
from app.schemas.agent import AgentConfig
from app.core.agent_manager import get_agent_manager
import asyncio
import logging
import secrets
import time
from typing import Optional
from app.schemas.web_socket import TokenResponse

logger = logging.getLogger(__name__)

router = APIRouter()
ws_tokens: dict[str, tuple[str, str, float]] = {}  # token: (api_key, agent_id, expire_at)
TOKEN_LIFETIME = 10

@router.get("/get_ws_token")
async def get_ws_token(api_key: str = Depends(get_api_key), agent_id: str = Query(...)):
    clean_expired_tokens()
    token = secrets.token_urlsafe(16)
    expire_at = time.time() + TOKEN_LIFETIME
    ws_tokens[token] = (api_key, agent_id, expire_at)
    return TokenResponse(token=token, expire_in=TOKEN_LIFETIME)

@router.websocket("/stream_voice")
async def websocket_stream_voice(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    llm_service: LLMService = Depends(get_llm_service),
    stt_service: STTService = Depends(get_stt_service),
    tts_service: TTSService = Depends(get_tts_service),
):
    clean_expired_tokens()
    if not token or token not in ws_tokens:
        await websocket.close(code=1008)
        return
    api_key, agent_id, expire_at = ws_tokens[token]
    if time.time() > expire_at:
        del ws_tokens[token]
        await websocket.close(code=1008)
        return
    del ws_tokens[token]
    await websocket.accept()
    await websocket.send_text(
        f"Hello! Connected with token associated to API key: {api_key} and agent ID: {agent_id}"
    )
    try:
        while True:
            data = await websocket.receive_json()
            client_token = data.get("token")
            client_timestamp = data.get("timestamp")
            audio_data = data.get("audio_data")

            # エージェント設定を取得
            agent_manager = get_agent_manager()
            agent_config = agent_manager.get_agent(agent_id)

            # STTサービスで音声ストリームを処理
            text = await stt_service.process_voice_stream(audio_data, agent_config)
            if text:
                # LLM処理
                llm_response = await llm_service.generate_response("voice", text, agent_config)
                # TTS処理
                audio_response = await tts_service.generate_speech(llm_response.agent_message, agent_config)
                # レスポンス送信
                await websocket.send_bytes(audio_response)
    except WebSocketDisconnect:
        await websocket.close()
    except Exception as e:
        logger.error(f"Error in handle_voice_stream: {str(e)}")
        await websocket.close()

def clean_expired_tokens():
    now = time.time()
    expired = [t for t, (_, _, exp) in ws_tokens.items() if exp < now]
    for t in expired:
        del ws_tokens[t]