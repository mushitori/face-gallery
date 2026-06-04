from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

from sqlalchemy.exc import OperationalError

T = TypeVar("T")

_MAX_ATTEMPTS = 12
_BASE_DELAY_SEC = 0.05


def is_locked_error(exc: BaseException) -> bool:
    return "locked" in str(exc).lower()


def run_with_retry(fn: Callable[[], T], *, attempts: int = _MAX_ATTEMPTS) -> T:
    """Retry SQLite operations that fail with database is locked."""
    last: BaseException | None = None
    for attempt in range(attempts):
        try:
            return fn()
        except OperationalError as exc:
            last = exc
            if not is_locked_error(exc) or attempt >= attempts - 1:
                raise
            time.sleep(_BASE_DELAY_SEC * (2**attempt))
    assert last is not None
    raise last
