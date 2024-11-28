from fastapi import APIRouter, Depends, HTTPException, Response
from app.auth.api_key import get_api_key
from app.core.agent_manager import get_agent_manager
from app.core.llm_service import LLMService
from app.core.tts_service import TTSService
from app.schemas.agent import ChatRequest, AgentResponse

router = APIRouter()
llm_service = LLMService()
tts_service = TTSService()

@router.post("/chat")
async def chat(request: ChatRequest, api_key: str = Depends(get_api_key)):
    """
    チャットエンドポイント
    音声データ（WAV形式）を返します
    """
    agent_manager = get_agent_manager()
    agent_config = agent_manager.get_agent(request.agent_id)
    
    if not agent_config:
        raise HTTPException(
            status_code=404,
            detail=f"Agent ID {request.agent_id} not found"
        )

    try:
        llm_response = await llm_service.generate_response(
            request.message, 
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
