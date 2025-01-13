# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.status import HTTP_403_FORBIDDEN
from app.core.config import get_settings, Settings


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    settings: Settings = Depends(get_settings),
):
    token = credentials.credentials

    if token is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="API key is required"
        )

    if not settings.api_keys:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="No API keys configured"
        )

    if not settings.is_valid_api_key(token):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API key")
    return token
