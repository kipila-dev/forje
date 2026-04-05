from functools import wraps


def require_context(func):
    """
    Ensures a method is only called within an active context.

    Raises:
        RuntimeError: If the method is called while the instance's
            `_active` attribute is False or missing.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not getattr(self, "_active", False):
            raise RuntimeError(f"'{func.__name__}' requires an active 'with' context.")
        return func(self, *args, **kwargs)

    return wrapper
