# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from pydantic import BaseModel
from typing import Literal

RequestType = Literal["text", "audio", "image_text", "image_audio"]
ResponseType = Literal["text", "audio"]


class BaseRequest(BaseModel):
    request_type: RequestType
    responce_type: str
    agent_id: str


class TextRequest(BaseRequest):
    request_type: Literal["text"] = "text"  # type: ignore
    text: str


class AudioRequest(BaseRequest):
    request_type: Literal["audio"] = "audio"  # type: ignore
    audio: str


class ImageTextRequest(BaseRequest):
    request_type: Literal["image_text"] = "image_text"  # type: ignore
    text: str
    image: str


class ImageAudioRequest(BaseRequest):
    request_type: Literal["image_audio"] = "image_audio"  # type: ignore
    audio: str
    image: str


class BaseResponse(BaseModel):
    responce_type: ResponseType


class TextResponse(BaseResponse):
    responce_type: Literal["text"] = "text"  # type: ignore
    user_message: str
    agent_message: str
    emotion: str


class AudioResponse(TextResponse):
    responce_type: Literal["audio"] = "audio"  # type: ignore
    audio_url: str
    duration: int


class TokenResponse(BaseModel):
    token: str
    expire_in: int
