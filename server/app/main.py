from fastapi import FastAPI, Depends
from app.auth.api_key import get_api_key
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import chat, line, agents
from app.core.config import get_settings
import logging

logging.basicConfig(
    level=logging.INFO,
)

settings = get_settings()
app = FastAPI(
    title="Karakuri_agentAPI",
    description="Karakuri_agentAPI",
    version="0.1.5+10"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    chat.router,
    prefix="/v1/chat",
    tags=["chat"]
)

app.include_router(
    line.router,
    prefix="/v1/line",
    tags=["line"]
)

app.include_router(
    agents.router,
    prefix="/v1",
    tags=["agents"]
)

@app.get("/health")
async def health_check(api_key: str = Depends(get_api_key)):
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}
