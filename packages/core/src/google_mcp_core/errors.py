from __future__ import annotations

from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

from googleapiclient.errors import HttpError


@dataclass
class MCPError(Exception):
    code: str
    message: str
    details: Optional[Any] = None

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


def normalize_google_error(error: Exception) -> MCPError:
    if isinstance(error, MCPError):
        return error
    if isinstance(error, HttpError):
        status = getattr(error.resp, "status", None)
        code = f"google_http_{status}" if status else "google_http_error"
        return MCPError(code=code, message=str(error), details=getattr(error, "content", None))
    return MCPError(code="unknown_error", message=str(error))


T = TypeVar('T')


def handle_google_api_error(func: Callable[..., T]) -> Callable[..., T]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise normalize_google_error(e)
    return wrapper
