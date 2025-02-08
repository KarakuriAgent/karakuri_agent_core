# Copyright (c) 0235 Inc.
# This file is licensed under the karakuri_agent Personal Use & No Warranty License.
# Please see the LICENSE file in the project root.

"""
Logging utility module.
Provides decorators and utilities for error handling and logging.
"""
import functools
import logging
from typing import Callable, TypeVar, Awaitable, Any, cast, ParamSpec, Dict
from app.core.exceptions import KarakuriError

T = TypeVar("T", bound=Callable[..., Awaitable[Any]])
P = ParamSpec("P")
logger = logging.getLogger(__name__)


def _sanitize_context(context: Dict) -> Dict:
    """
    Sanitize sensitive data in error context.
    
    Args:
        context: Dictionary containing error context
        
    Returns:
        Dictionary with sensitive data sanitized
    """
    sensitive_keys = ['user_id', 'agent_id', 'api_key']
    sanitized = context.copy()
    for key in sensitive_keys:
        if key in sanitized and sanitized[key]:
            value = str(sanitized[key])
            sanitized[key] = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
    return sanitized


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
                "function": func.__name__
            }
            # Add context to error
            e.context.update(context)
            # Log error with sanitized context
            sanitized_context = _sanitize_context(e.context)
            logger.error(f"{str(e)} | Context: {sanitized_context}")
            raise
        except Exception as e:
            # Convert unknown errors to KarakuriError
            context = {
                "agent_id": kwargs.get("agent_id"),
                "user_id": kwargs.get("user_id"),
                "original_error": str(e),
                "function": func.__name__
            }
            sanitized_context = _sanitize_context(context)
            logger.error(f"Unexpected error: {str(e)} | Context: {sanitized_context}")
            raise KarakuriError(
                message=f"An unexpected error occurred: {str(e)}",
                context=context
            ) from e

    return cast(T, wrapper)
