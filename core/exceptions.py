"""Global exception handlers for the FastAPI application."""

import logging

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unhandled exceptions."""
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


def register_exception_handlers(app):
    """Register all exception handlers on the FastAPI app."""
    app.add_exception_handler(Exception, generic_exception_handler)
