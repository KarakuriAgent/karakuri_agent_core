# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.

from typing import List
from pydantic import BaseModel
from app.schemas.chat_message import ChatMessage


class PendingMessageContext(BaseModel):
    base_url: str
    message_type: str
    chat_messages: List[ChatMessage]
