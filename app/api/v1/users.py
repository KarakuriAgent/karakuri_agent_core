# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from fastapi import APIRouter, Depends, HTTPException
from app.auth.api_key import verify_token
from app.schemas.user import UserResponse
from app.core.user_manager import get_user_manager
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/users")
async def list_users(api_key: str = Depends(verify_token)):
    try:
        user_manager = get_user_manager()
        users = user_manager.get_all_users()
        return [
            UserResponse(user_id=id, display_name=display_name)
            for id, display_name in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")
