import logging
import traceback
from datetime import datetime, timezone
from fastapi import Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


def _error_body(code: str, message: str, details=None) -> dict:
    return {
        "status": "error",
        "code": code,
        "message": message,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "details": details,
    }


def error_response(code: str, message: str, status_code: int, details=None) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=_error_body(code, message, details))


class HandledRoute(APIRoute):
    """
    Custom route class that acts as a centralized error handler for all endpoints.
    - Catches AppException and maps it to a structured JSON error response.
    - Catches unhandled exceptions, logs the full traceback at DEBUG level,
      and returns a generic 500 response.
    Apply by setting route_class=HandledRoute on any APIRouter.
    """

    def get_route_handler(self):
        original = super().get_route_handler()

        async def handler(request: Request) -> Response:
            try:
                return await original(request)
            except AppException as exc:
                logger.warning("[%s] %s", exc.code, exc.message)
                return error_response(exc.code, exc.message, exc.status_code, exc.details)
            except RequestValidationError as exc:
                logger.debug("Validation error: %s", exc.errors())
                return error_response("VALIDATION_ERROR", "Request validation failed.", 422, exc.errors())
            except Exception as exc:
                logger.debug("Unhandled exception:\n%s", traceback.format_exc())
                logger.error("Internal server error: %s", exc)
                return error_response(
                    "INTERNAL_SERVER_ERROR",
                    "An unexpected error occurred.",
                    500,
                )

        return handler
