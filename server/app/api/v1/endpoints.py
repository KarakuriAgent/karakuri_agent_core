from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File
from app.auth.api_key import get_api_key
from app.core.agent_manager import get_agent_manager
from app.core.llm_service import LLMService
from app.core.tts_service import TTSService
from app.schemas.agent import AgentResponse
from app.core.stt_service import STTService

router = APIRouter()
llm_service = LLMService()
stt_service = STTService()
tts_service = TTSService()

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
