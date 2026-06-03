from __future__ import annotations

import functools
import logging
import time
from typing import Any, Callable, TypeVar

logger = logging.getLogger("autosalon.audit")

F = TypeVar("F", bound=Callable[..., Any])


def audit(action: str) -> Callable[[F], F]:

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.info("action=%s elapsed_ms=%.3f", action, elapsed_ms)

        return wrapper

    return decorator
