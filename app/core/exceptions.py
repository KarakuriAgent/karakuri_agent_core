# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.

"""
Custom exception classes for the Karakuri Agent application.
This module defines a hierarchy of exceptions for different types of errors that can occur.
"""

from typing import Optional


class KarakuriError(Exception):
    """
    Base exception class for all Karakuri Agent errors.
    Provides context and error message handling capabilities.
    """

    def __init__(
        self, message: str, status_code: int = 500, context: Optional[dict] = None
    ):
        self.message = message
        self.status_code = status_code
        self.context = context or {}
        super().__init__(self.message)


class UserError(KarakuriError):
    """
    Exception raised for errors that are caused by user input or user-related operations.
    Examples include invalid input data, authentication failures, or permission issues.
    """

    def __init__(self, message: str, context: Optional[dict] = None):
        super().__init__(message, status_code=400, context=context)


class AgentError(KarakuriError):
    """
    Exception raised for errors related to agent operations.
    Examples include agent configuration issues or agent state management problems.
    """

    def __init__(self, message: str, context: Optional[dict] = None):
        super().__init__(message, status_code=500, context=context)


class LLMError(KarakuriError):
    """
    Exception raised for errors that occur during LLM (Language Learning Model) operations.
    Examples include API failures, token limit exceeded, or invalid model responses.
    """

    def __init__(self, message: str, context: Optional[dict] = None):
        super().__init__(message, status_code=503, context=context)


class AudioProcessingError(KarakuriError):
    """
    Exception raised for errors during audio processing operations.
    Examples include TTS/STT failures, invalid audio format, or provider-specific issues.
    """

    def __init__(self, message: str, context: Optional[dict] = None):
        super().__init__(message, status_code=500, context=context)


class ChatError(KarakuriError):
    """
    Exception raised for errors that occur during chat operations.
    Examples include message delivery failures or chat session management issues.
    """

    def __init__(self, message: str, context: Optional[dict] = None):
        super().__init__(message, context=context)


class KarakuriMemoryError(KarakuriError):
    """
    Exception raised for errors related to memory operations.
    Examples include memory storage failures, retrieval issues, or memory context problems.
    """

    def __init__(self, message: str, context: Optional[dict] = None):
        super().__init__(message, context=context)
