from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import endpoints
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
    endpoints.router,
    prefix="/v1",
    tags=["v1"]
)

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}
