# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from pydantic import BaseModel


class TextResponse(BaseModel):
    text: str


class VoiceResponse(BaseModel):
    audio_url: str
    duration: int
