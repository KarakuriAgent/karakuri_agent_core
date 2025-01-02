from enum import Enum
from pydantic import BaseModel


class CommunicationChannel(str, Enum):
    CHAT = "chat"  # Text-based communication (LINE, etc.)
    VOICE = "voice"  # Voice communication
    VIDEO = "video"  # Video communication (for future expansion)


class AgentStatus(str, Enum):
    AVAILABLE = "available"  # Free and ready to interact
    SLEEPING = "sleeping"  # Currently sleeping
    EATING = "eating"  # Having a meal
    WORKING = "working"  # Working on tasks but can handle chat
    OUT = "out"  # Outside/Away but can handle chat
    MAINTENANCE = "maintenance"  # System maintenance mode


class StatusAvailability(BaseModel):
    chat: bool
    voice: bool
    video: bool


# Define communication availability for each status
STATUS_AVAILABILITY = {
    AgentStatus.AVAILABLE: StatusAvailability(chat=True, voice=True, video=True),
    AgentStatus.SLEEPING: StatusAvailability(chat=False, voice=False, video=False),
    AgentStatus.EATING: StatusAvailability(chat=True, voice=False, video=False),
    AgentStatus.WORKING: StatusAvailability(chat=True, voice=False, video=False),
    AgentStatus.OUT: StatusAvailability(chat=True, voice=False, video=False),
    AgentStatus.MAINTENANCE: StatusAvailability(chat=False, voice=False, video=False),
}


class AgentStatusConfig(BaseModel):
    current_status: AgentStatus
    last_status_change: str  # ISO format datetime
    next_status_change: str | None = None  # ISO format datetime
    status_message: str | None = None
