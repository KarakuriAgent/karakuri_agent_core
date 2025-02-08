# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import talk, line, agents, users, web_socket, openai
from app.auth.api_key import verify_token
from app.core.config import get_settings
from app.core.tasks.status_check import check_conversation_timeouts
from app.core.tasks.message_sender import send_pending_messages
from contextlib import asynccontextmanager
import asyncio
import logging
from app.core.exceptions import KarakuriError
from app.middleware.error_handler import karakuri_exception_handler
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logging.basicConfig(
    level=logging.INFO,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    status_check_task = asyncio.create_task(check_conversation_timeouts())
    message_sender_task = asyncio.create_task(send_pending_messages())
    yield
    status_check_task.cancel()
    message_sender_task.cancel()
    try:
        await status_check_task
        await message_sender_task
    except asyncio.CancelledError:
        logging.info("Background tasks were cancelled")


app = FastAPI(
    title="Karakuri_agentAPI",
    description="Karakuri_agentAPI",
    version="0.3.0+13",
    lifespan=lifespan,
)


# Register error handlers
@app.exception_handler(KarakuriError)
async def handle_karakuri_error(request: Request, exc: KarakuriError) -> JSONResponse:
    return await karakuri_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "error": "ValidationError",
            "detail": str(exc),
            "context": {"path": request.url.path, "method": request.method},
        },
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(talk.router, prefix="/v1/talk", tags=["talk"])

app.include_router(openai.router, prefix="/v1", tags=["openai"])

app.include_router(line.router, prefix="/v1/line", tags=["line"])

app.include_router(agents.router, prefix="/v1", tags=["agents"])

app.include_router(web_socket.router, prefix="/v1/ws", tags=["websocket"])

app.include_router(users.router, prefix="/v1", tags=["users"])


@app.get("/health")
async def health_check(api_key: str = Depends(verify_token)):
    return {"status": "healthy"}
