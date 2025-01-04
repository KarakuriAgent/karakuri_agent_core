# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from app.auth.api_key import get_api_key
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import chat, line, agents, web_socket, status
from app.core.config import get_settings
import logging

from app.dependencies import get_schedule_service

logging.basicConfig(
    level=logging.INFO,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global schedule_service
    schedule_service = get_schedule_service()
    await schedule_service.initialize()

    yield

    if schedule_service:
        await schedule_service.stop_schedule_generation()
        await schedule_service.stop_schedule_execution()


app = FastAPI(
    title="Karakuri_agentAPI",
    description="Karakuri_agentAPI",
    version="0.2.1+12",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/v1/chat", tags=["chat"])

app.include_router(line.router, prefix="/v1/line", tags=["line"])

app.include_router(agents.router, prefix="/v1", tags=["agents"])

app.include_router(web_socket.router, prefix="/v1/ws", tags=["websocket"])

app.include_router(status.router, prefix="/v1", tags=["status"])


@app.get("/health")
async def health_check(api_key: str = Depends(get_api_key)):
    return {"status": "healthy"}
