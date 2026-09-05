"""
Custom exceptions and a shared error response shape.

Every error the API returns follows the same JSON envelope so the frontend
can handle errors generically instead of special-casing each endpoint.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse


class OpsPilotError(Exception):
    """Base class for all application-raised errors."""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(OpsPilotError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class UnauthorizedError(OpsPilotError):
    def __init__(self, message: str = "Not authenticated"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(OpsPilotError):
    def __init__(self, message: str = "You don't have permission to do that"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class ValidationError(OpsPilotError):
    def __init__(self, message: str = "Invalid input"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


async def opspilot_exception_handler(request: Request, exc: OpsPilotError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"message": exc.message, "type": exc.__class__.__name__}},
    )
