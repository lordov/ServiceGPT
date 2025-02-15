from typing import Optional
from fastapi import HTTPException, status

from app.core.exceptions.schemas import ErrorResponseModel


class CustomHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: str, errors: list[str] = None):
        super().__init__(status_code=status_code, detail=detail)
        self.errors = errors

    def dict(self):
        return ErrorResponseModel(
            status_code=self.status_code,
            detail=self.detail,
            errors=self.errors
        ).model_dump()


class UserNotFoundException(HTTPException):
    def __init__(self, errors: Optional[list[str]] = None):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        self.errors = errors


class UserAlreadyExists(HTTPException):
    def __init__(self, errors: Optional[list[str]] = None):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail="This user already exist")
        self.errors = errors


class AlreadyExistError(Exception):
    pass


class DBError(Exception):
    pass


class NoRowsFoundError(CustomHTTPException):
    def __init__(self, detail: str, errors: Optional[list[str]] = None):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, errors=errors)


class MultipleRowsFoundError(CustomHTTPException):
    def __init__(self, detail: str, errors: Optional[list[str]] = None):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail, errors=errors)


class TokenError(Exception):
    pass
