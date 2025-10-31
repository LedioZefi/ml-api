"""Structured logging configuration with JSON formatter and request ID middleware."""
import json
import logging
import logging.config
import uuid
from collections.abc import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


def configure_logging() -> None:
    """Configure structured JSON logging to stdout."""
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "app.logging_config.JSONFormatter",
            },
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": True,
            },
        },
    }
    logging.config.dictConfig(config)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as single-line JSON."""
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID tracking."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add request ID to request and response headers."""
        # Read X-Request-ID or generate a short UUID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])

        # Store in request state for logging
        request.state.request_id = request_id

        # Log request
        logger = logging.getLogger("app.request")
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={"request_id": request_id},
        )

        # Call next middleware/endpoint
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} {response.status_code}",
            extra={"request_id": request_id},
        )

        return response


async def add_request_id_middleware(request: Request, call_next: Callable) -> Response:
    """Middleware function to add request ID tracking."""
    # Read X-Request-ID or generate a short UUID
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])

    # Store in request state for logging
    request.state.request_id = request_id

    # Log request
    logger = logging.getLogger("app.request")
    logger.info(
        f"{request.method} {request.url.path}",
        extra={"request_id": request_id},
    )

    # Call next middleware/endpoint
    response = await call_next(request)

    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id

    # Log response
    logger.info(
        f"{request.method} {request.url.path} {response.status_code}",
        extra={"request_id": request_id},
    )

    return response

