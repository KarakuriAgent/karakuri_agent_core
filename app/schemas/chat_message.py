# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"


class MessageContent(BaseModel):
    type: MessageType
    text: Optional[str] = None
    image: Optional[bytes] = None


class ChatMessage(BaseModel):
    reply_token: str
    content: MessageContent
    id: str
    timestamp: datetime
