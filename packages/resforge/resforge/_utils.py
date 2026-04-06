from collections.abc import Callable
from functools import wraps
from typing import Concatenate


def require_context[T, **P, R](
    func: Callable[Concatenate[T, P], R],
) -> Callable[Concatenate[T, P], R]:
    """Ensures a method is only called within an active context.

    Raises:
        RuntimeError: If the method is called while the instance's
            `_active` attribute is False or missing.

    """

    @wraps(func)
    def wrapper(self: T, *args: P.args, **kwargs: P.kwargs) -> R:
        if not getattr(self, "_active", False):
            msg = f"'{func.__name__}' requires an active 'with' context."
            raise RuntimeError(msg)
        return func(self, *args, **kwargs)

    return wrapper
