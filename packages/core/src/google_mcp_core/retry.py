from __future__ import annotations

import random
import time
from typing import Callable, TypeVar

from googleapiclient.errors import HttpError

T = TypeVar("T")


RETRIABLE_STATUSES = {429, 500, 502, 503, 504}


def execute_with_retry(
    fn: Callable[[], T],
    retries: int = 3,
    initial_backoff: float = 0.5,
    backoff_multiplier: float = 2.0,
) -> T:
    attempt = 0
    backoff = initial_backoff
    while True:
        try:
            return fn()
        except HttpError as exc:
            status = getattr(exc.resp, "status", None)
            if status not in RETRIABLE_STATUSES or attempt >= retries:
                raise
        except Exception:
            if attempt >= retries:
                raise
        sleep_for = backoff * (1 + random.random())
        time.sleep(sleep_for)
        attempt += 1
        backoff *= backoff_multiplier
