from __future__ import annotations

from typing import Callable, Iterable, Optional, Sequence, Tuple, TypeVar

T = TypeVar("T")


def paginate(
    request_fn: Callable[[Optional[str], Optional[int]], Tuple[Sequence[T], Optional[str]]],
    page_token: Optional[str] = None,
    limit: Optional[int] = None,
) -> Tuple[list[T], Optional[str]]:
    items, next_token = request_fn(page_token, limit)
    return list(items), next_token
