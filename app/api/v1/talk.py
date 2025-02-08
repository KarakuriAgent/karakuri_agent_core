# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, Request
from app.dependencies import (
    get_talk_facade,
)
from app.auth.api_key import verify_token
from app.core.facade.talk_facade import TalkFacade
from starlette.responses import FileResponse
from pathlib import Path
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()
UPLOAD_DIR = settings.talk_audio_files_dir
MAX_FILES = settings.talk_max_audio_files


@router.post("/text/text")
async def talk_text_to_text(
    request: Request,
    agent_id: str = Form(...),
    user_id: str = Form(...),
    message: str = Form(...),
    image_file: Optional[UploadFile] = None,
    api_key: str = Depends(verify_token),
    talk_facade: TalkFacade = Depends(get_talk_facade),
):
    return await talk_facade.handle_agent_response(
        request=request,
        agent_id=agent_id,
        user_id=user_id,
        message=message,
        image_file=image_file,
        generate_voice=False,
    )


@router.post("/text/voice")
async def talk_text_to_voice(
    request: Request,
    agent_id: str = Form(...),
    user_id: str = Form(...),
    message: str = Form(...),
    image_file: Optional[UploadFile] = None,
    api_key: str = Depends(verify_token),
    talk_facade: TalkFacade = Depends(get_talk_facade),
):
    return await talk_facade.handle_agent_response(
        request=request,
        agent_id=agent_id,
        user_id=user_id,
        message=message,
        image_file=image_file,
        generate_voice=True,
    )


@router.post("/voice/text")
async def talk_voice_to_text(
    request: Request,
    agent_id: str = Form(...),
    user_id: str = Form(...),
    image_file: Optional[UploadFile] = None,
    audio_file: UploadFile = File(...),
    api_key: str = Depends(verify_token),
    talk_facade: TalkFacade = Depends(get_talk_facade),
):
    audio_content = await audio_file.read()

    return await talk_facade.handle_agent_response(
        request=request,
        agent_id=agent_id,
        user_id=user_id,
        message=audio_content,
        image_file=image_file,
        generate_voice=False,
    )


@router.post("/voice/voice")
async def talk_voice_to_voice(
    request: Request,
    agent_id: str = Form(...),
    user_id: str = Form(...),
    image_file: Optional[UploadFile] = None,
    audio_file: UploadFile = File(...),
    api_key: str = Depends(verify_token),
    talk_facade: TalkFacade = Depends(get_talk_facade),
):
    audio_content = await audio_file.read()

    return await talk_facade.handle_agent_response(
        request=request,
        agent_id=agent_id,
        user_id=user_id,
        message=audio_content,
        image_file=image_file,
        generate_voice=True,
    )


@router.get(f"/{UPLOAD_DIR}/{{file_name}}")
async def get_audio(file_name: str):
    if ".." in file_name or "/" in file_name:
        raise HTTPException(status_code=400, detail="Invalid file name")
    file_path = Path(f"{UPLOAD_DIR}/{file_name}.wav")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path)
