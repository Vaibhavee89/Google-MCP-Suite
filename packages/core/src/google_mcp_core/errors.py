from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

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
