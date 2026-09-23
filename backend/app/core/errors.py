"""Structured API errors (PRD §29).

Internal details (stack traces, SQL, keys, paths) are NEVER returned —
only a code + a human-readable message.
"""

from fastapi import Request
from fastapi.responses import JSONResponse


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status,
        content={"code": exc.code, "message": exc.message},
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    # Log server-side; return a sanitized message to the client.
    import logging

    logging.getLogger("rams").exception("Unhandled error")
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_ERROR",
            "message": "Something went wrong. Please try again.",
        },
    )
