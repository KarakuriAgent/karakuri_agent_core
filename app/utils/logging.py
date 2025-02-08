# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.

"""
Logging utility module.
Provides decorators and utilities for error handling and logging.
"""

import functools
import logging
from typing import Callable, TypeVar, Awaitable, Any, cast, ParamSpec
from app.core.exceptions import KarakuriError

T = TypeVar("T", bound=Callable[..., Awaitable[Any]])
P = ParamSpec("P")
logger = logging.getLogger(__name__)


def error_handler(func: T) -> T:
    """
    A decorator that handles errors and logs them with context.

    Args:
        func: The function to decorate

    Returns:
        wrapper: The decorated function with error handling capabilities
    """

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except KarakuriError as e:
            # Extract error context
            context = {
                "agent_id": kwargs.get("agent_id"),
                "user_id": kwargs.get("user_id"),
                "error_type": e.__class__.__name__,
                "function": func.__name__,
            }
            # Add context to error
            e.context.update(context)
            # Log error with context
            logger.error(f"{str(e)} | Context: {e.context}")
            raise
        except Exception as e:
            # Convert unknown errors to KarakuriError
            context = {
                "agent_id": kwargs.get("agent_id"),
                "user_id": kwargs.get("user_id"),
                "original_error": str(e),
                "function": func.__name__,
            }
            logger.error(f"Unexpected error: {str(e)} | Context: {context}")
            raise KarakuriError(
                message=f"An unexpected error occurred: {str(e)}", context=context
            ) from e

    return cast(T, wrapper)
