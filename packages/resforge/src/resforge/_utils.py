import os
from collections.abc import Callable, Generator
from contextlib import contextmanager, suppress
from functools import wraps
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import IO, Concatenate


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


@contextmanager
def atomic_write(target_path: Path) -> Generator[IO[bytes], None, None]:
    """Yields a temporary file, then atomically replaces target_path on success."""
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = None
    try:
        with NamedTemporaryFile(
            dir=target_path.parent, delete=False, suffix=".tmp"
        ) as tf:
            temp_path = Path(tf.name)
            yield tf

            tf.flush()
            os.fsync(tf.fileno())

        temp_path.replace(target_path)

        if os.name == "posix":
            flags = os.O_RDONLY
            if hasattr(os, "O_DIRECTORY"):
                flags |= os.O_DIRECTORY
            dir_fd = os.open(target_path.parent, flags)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
    finally:
        if temp_path and temp_path.exists():
            with suppress(OSError):
                temp_path.unlink()
