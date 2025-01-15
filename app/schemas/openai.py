from typing import List
from litellm import AllMessageValues, Required, TypedDict
from typing import Optional, Dict


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


class StreamChatCompletionResponse(TypedDict, total=False):
    id: str
    created: int
    model: Optional[str]
    object: str
    system_fingerprint: Optional[str]
    choices: List[Choice]
    stream_options: Optional[Dict]
