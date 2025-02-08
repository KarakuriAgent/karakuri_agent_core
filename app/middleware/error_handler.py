"""
Error handling middleware for FastAPI.
Provides centralized error handling for the application.
"""

import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import KarakuriError

logger = logging.getLogger(__name__)


async def karakuri_exception_handler(
    request: Request, exc: KarakuriError
) -> JSONResponse:
    """
    Global exception handler for KarakuriError.
    Converts exceptions to JSON responses with appropriate status codes and context.

    Args:
        request: FastAPI request object
        exc: KarakuriError instance

    Returns:
        JSONResponse: Error response with status code and context
    """
    error_response = {
        "error": exc.__class__.__name__,
        "message": str(exc),
        "context": exc.context,
    }

    logger.error(f"Error handled: {error_response}")
    return JSONResponse(
        status_code=getattr(exc, "status_code", 500), content=error_response
    )
