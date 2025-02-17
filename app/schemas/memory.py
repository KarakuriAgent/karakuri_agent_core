# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.

from typing import Optional
from litellm import AllMessageValues
from pydantic import BaseModel


class KarakuriMemory(BaseModel):
    messages: list[AllMessageValues]
    facts: Optional[str]
    context: str
