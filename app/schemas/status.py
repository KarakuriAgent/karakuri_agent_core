# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from datetime import datetime
from typing import Literal, Optional, Union
from enum import Enum
from pydantic import BaseModel


class StatusType(Enum):
    ACTIVE = "ACTIVE"
    TALKING = "TALKING"
    RESTING = "RESTING"
    SLEEPING = "SLEEPING"


class AgentStatus(BaseModel):
    description: str
    started_at: datetime
    end_at: Optional[datetime]
    is_chat_available: bool


class ActiveStatusData(AgentStatus):
    location: str
    type: Literal[StatusType.ACTIVE] = StatusType.ACTIVE


class TalkingStatusData(AgentStatus):
    user_id: str
    type: Literal[StatusType.TALKING] = StatusType.TALKING
    is_chat_available: bool = False
    last_conversation_time: Optional[datetime] = None


class RestingStatusData(AgentStatus):
    location: str
    type: Literal[StatusType.RESTING] = StatusType.RESTING
    is_chat_available: bool = True


class SleepingStatusData(AgentStatus):
    location: str = "bead room"
    type: Literal[StatusType.SLEEPING] = StatusType.SLEEPING
    is_chat_available: bool = False
    pass


Status = Union[
    ActiveStatusData, TalkingStatusData, RestingStatusData, SleepingStatusData
]
