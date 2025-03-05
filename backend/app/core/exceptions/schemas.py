from typing import Optional
from pydantic import BaseModel


class ErrorResponseModel(BaseModel):
    status_code: int
    detail: str
    errors: Optional[list[str]] = None
