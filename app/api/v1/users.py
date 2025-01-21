# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from fastapi import APIRouter, Depends, HTTPException
from app.auth.api_key import verify_token
from app.schemas.user import UserResponse
from app.core.memory_service import MemoryService
from app.dependencies import get_memory_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=UserResponse)
async def add_user(
    user_id: str,
    memory_service: MemoryService = Depends(get_memory_service),
    _: None = Depends(verify_token),
):
    """Add a new user."""
    try:
        await memory_service.add_user(user_id)
        return {"user_id": user_id}
    except Exception as e:
        logger.error(f"Failed to add user: {e}")
        raise HTTPException(status_code=500, detail="Failed to add user")


@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: str,
    memory_service: MemoryService = Depends(get_memory_service),
    _: None = Depends(verify_token),
):
    """Delete a user."""
    try:
        await memory_service.delete_user(user_id)
        return {"user_id": user_id}
    except Exception as e:
        logger.error(f"Failed to delete user: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    memory_service: MemoryService = Depends(get_memory_service),
    _: None = Depends(verify_token),
):
    """Get user information."""
    try:
        return await memory_service.get_user(user_id)
    except Exception as e:
        logger.error(f"Failed to get user: {e}")
        raise HTTPException(status_code=404, detail="User not found")


@router.get("", response_model=list[UserResponse])
async def list_users(
    memory_service: MemoryService = Depends(get_memory_service),
    _: None = Depends(verify_token),
):
    """List all users."""
    try:
        return await memory_service.list_users()
    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        raise HTTPException(status_code=500, detail="Failed to list users")
