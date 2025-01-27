# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.
from typing import TypedDict
from pydantic import BaseModel


class LLMResponse(BaseModel):
    user_message: str
    agent_message: str
    emotion: str


class ToolParameter(TypedDict):
    type: str
    description: str


class ToolParameterProperties(TypedDict):
    query: ToolParameter


class ToolParameterDefinition(TypedDict):
    type: str
    properties: ToolParameterProperties
    required: list[str]


class ToolFunction(TypedDict):
    name: str
    description: str
    parameters: ToolParameterDefinition


class ToolDefinition(TypedDict):
    type: str
    function: ToolFunction


class ToolCallFunction(TypedDict):
    name: str
    arguments: str


class ToolCall(TypedDict):
    function: ToolCallFunction
