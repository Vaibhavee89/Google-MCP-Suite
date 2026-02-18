from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class NormalizedUser:
    email: Optional[str] = None
    display_name: Optional[str] = None
    resource_id: Optional[str] = None


@dataclass
class NormalizedAttachment:
    name: str
    mime_type: Optional[str] = None
    size: Optional[int] = None
    reference: Optional[str] = None
