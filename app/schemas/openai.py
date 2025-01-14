from typing import List

from litellm import AllMessageValues, Required, TypedDict


class ChatCompletionRequest(TypedDict, total=False):
    model: Required[str]
    messages: Required[List[AllMessageValues]]
    stream: Required[bool]
