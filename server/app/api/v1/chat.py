from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File
from app.dependencies import get_llm_service, get_tts_service, get_stt_service
from app.auth.api_key import get_api_key
from app.core.agent_manager import get_agent_manager
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/text/text")
async def chat_text_to_text(
    agent_id: str, 
    message: str, 
    api_key: str = Depends(get_api_key),
    llm_service = Depends(get_llm_service),
):
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
        return Response(content=json.dumps(llm_response, ensure_ascii=False))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@router.post("/text/voice")
async def chat_text_to_voice(
    agent_id: str, 
    message: str, 
    api_key: str = Depends(get_api_key),
    llm_service = Depends(get_llm_service),
    tts_service = Depends(get_tts_service)
):
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
        message = llm_response["message"]

        audio_data = await tts_service.generate_speech(
            message, 
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

@router.post("/voice/text")
async def chat_voice_to_text(
    agent_id: str,
    audio_file: UploadFile = File(...),
    api_key: str = Depends(get_api_key),
    llm_service = Depends(get_llm_service),
    stt_service = Depends(get_stt_service)
):
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

        return Response(content=json.dumps(llm_response, ensure_ascii=False))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@router.post("/voice/voice")
async def chat_voice_to_voice(
    agent_id: str,
    audio_file: UploadFile = File(...),
    api_key: str = Depends(get_api_key),
    llm_service = Depends(get_llm_service),
    stt_service = Depends(get_stt_service),
    tts_service = Depends(get_tts_service)
):
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
        message = llm_response["message"]

        audio_data = await tts_service.generate_speech(
            message, 
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
