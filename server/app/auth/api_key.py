# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from fastapi import Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from typing import Optional
from app.core.config import get_settings, Settings

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(
    api_key_header: Optional[str] = Security(api_key_header),
    settings: Settings = Depends(get_settings)
) -> str:
    if api_key_header is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="API キーが必要です"
        )
    
    if not settings.api_keys:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="API キーが設定されていません"
        )
    
    if not settings.is_valid_api_key(api_key_header):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="無効なAPI キーです"
        )
    
    return api_key_header
