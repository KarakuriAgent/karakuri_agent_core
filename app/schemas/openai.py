# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from typing import List, AsyncGenerator, Optional, Dict, cast
import json
import logging
from litellm import AllMessageValues, Required, TypedDict, Choices
from litellm.files.main import ModelResponse
from app.utils.json_utils import convert_none_to_null

logger = logging.getLogger(__name__)


class ChatCompletionRequest(TypedDict, total=False):
    model: Required[str]
    messages: Required[List[AllMessageValues]]
    stream: Required[bool]


class DeltaContent(TypedDict, total=False):
    content: Optional[str]
    role: Optional[str]
    function_call: Optional[Dict]
    tool_calls: Optional[List]
    audio: Optional[Dict]


class Choice(TypedDict, total=False):
    finish_reason: Optional[str]
    index: int
    delta: DeltaContent
    logprobs: Optional[Dict]


class StreamChatCompletionResponse:
    def __init__(
        self,
        id: str,
        created: int,
        model: Optional[str],
        object: str,
        system_fingerprint: Optional[str],
        choices: List[Choice],
        stream_options: Optional[Dict] = None,
    ):
        self.id = id
        self.created = created
        self.model = model
        self.object = object
        self.system_fingerprint = system_fingerprint
        self.choices = choices
        self.stream_options = stream_options

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "created": self.created,
            "model": self.model,
            "object": self.object,
            "system_fingerprint": self.system_fingerprint,
            "choices": self.choices,
            "stream_options": self.stream_options,
        }

    @classmethod
    async def generate_stream(
        cls,
        response: "ModelResponse",
    ) -> AsyncGenerator[bytes, None]:
        try:
            if response:
                choice_list = []
                for choice in response.choices:
                    choices = cast(Choices, choice)
                    choice_obj = Choice(
                        finish_reason=choices.finish_reason,
                        index=choices.index,
                        delta=DeltaContent(
                            content=choices.message.content,
                            role=choices.message.role,
                            function_call=None,
                            tool_calls=choices.message.tool_calls,
                            audio=None,
                        ),
                        logprobs=None,
                    )
                    choice_list.append(choice_obj)

                response_data = cls(
                    id=response.id,
                    created=response.created,
                    model=response.model,
                    object=response.object,
                    system_fingerprint=response.system_fingerprint,
                    choices=choice_list,
                    stream_options=None,
                )
                yield f"data: {json.dumps(response_data.to_dict(), default=convert_none_to_null)}\n\n".encode(
                    "utf-8"
                )
        except Exception as e:
            logger.error(f"Error in stream generation: {str(e)}")
            yield f"data: [ERROR] {str(e)}\n\n".encode("utf-8")
        finally:
            yield b"data: [DONE]\n\n"
