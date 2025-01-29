# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
import logging
from app.core.config import get_settings
from app.core.valkey_client import ValkeyClient
from app.schemas.status import (
    ActiveStatusData,
    AgentStatus,
    RestingStatusData,
    SleepingStatusData,
    TalkingStatusData,
)
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
settings = get_settings()
_valkey_client = ValkeyClient(settings.valkey_url, settings.valkey_password)


class StatusService:
    async def update_current_status(self, agent_id: str, status: AgentStatus):
        await _valkey_client.update_current_status(agent_id, status)

    async def get_current_status(self, agent_id: str) -> AgentStatus:
        return await _valkey_client.get_current_status(agent_id)


def create_active_status(
    description: str,
    location: str,
    is_chat_available: bool,
    duration_minutes: int,
) -> ActiveStatusData:
    return ActiveStatusData(
        description=description,
        started_at=datetime.now(),
        end_at=datetime.now() + timedelta(minutes=duration_minutes),
        is_chat_available=is_chat_available,
        location=location,
    )


def create_talking_status(
    user_id: str,
    user_name: str,
) -> TalkingStatusData:
    return TalkingStatusData(
        description=f"Talking with {user_name}",
        started_at=datetime.now(),
        end_at=None,
        user_id=user_id,
        user_name=user_name,
    )


def create_resting_status(
    description: str,
    location: str,
    duration_minutes: int,
) -> RestingStatusData:
    return RestingStatusData(
        description=description,
        started_at=datetime.now(),
        end_at=datetime.now() + timedelta(minutes=duration_minutes),
        location=location,
    )


def create_sleeping_status(
    description: str,
    duration_minutes: int,
) -> SleepingStatusData:
    return SleepingStatusData(
        description=description,
        location="bead room",
        started_at=datetime.now(),
        end_at=datetime.now() + timedelta(minutes=duration_minutes),
    )
