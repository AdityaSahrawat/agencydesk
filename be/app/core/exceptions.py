from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class AgencyDeskException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, details: Optional[Any] = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class UnauthorizedException(AgencyDeskException):
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(AgencyDeskException):
    def __init__(self, message: str = "Permission denied for this tenant resource"):
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN)


class NotFoundException(AgencyDeskException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND)


class ConflictException(AgencyDeskException):
    def __init__(self, message: str = "Resource conflict or duplicate entry"):
        super().__init__(message=message, status_code=status.HTTP_409_CONFLICT)


def create_error_response(status_code: int, message: str, details: Optional[Any] = None) -> JSONResponse:
    payload = {
        "success": False,
        "error": {
            "code": status_code,
            "message": message,
        }
    }
    if details is not None:
        payload["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=payload)


async def agencydesk_exception_handler(request: Request, exc: AgencyDeskException):
    return create_error_response(exc.status_code, exc.message, exc.details)


async def http_exception_handler(request: Request, exc: HTTPException):
    return create_error_response(exc.status_code, exc.detail)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return create_error_response(
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "Validation error in request parameters or body",
        exc.errors()
    )


async def generic_exception_handler(request: Request, exc: Exception):
    return create_error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "An unexpected internal server error occurred",
        str(exc)
    )
