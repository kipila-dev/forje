import os
import shutil
from collections.abc import Generator
from contextlib import contextmanager, suppress
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import IO, Protocol, runtime_checkable

__all__ = ["FileSystemSink", "MemorySink", "WriteSink", "atomic_write"]


@contextmanager
def atomic_write(target_path: str | Path) -> Generator[IO[bytes], None, None]:
    """Yields a temporary file, then atomically replaces target_path on success.

    Preserves file permissions if `target_path` already exists.
    """
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = None
    try:
        with NamedTemporaryFile(
            dir=target_path.parent,
            delete=False,
            suffix=".tmp",
        ) as tf:
            temp_path = Path(tf.name)
            yield tf

            tf.flush()
            os.fsync(tf.fileno())

        try:
            shutil.copymode(target_path, temp_path)
        except OSError:
            mask = os.umask(0)
            os.umask(mask)
            temp_path.chmod(0o666 & ~mask)

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


@runtime_checkable
class WriteSink(Protocol):
    """An interface for writing binary content to a file path."""

    def write(self, path: Path, content: bytes) -> None:
        """Write the given binary content to the specified path."""
        ...


class FileSystemSink:
    """A write sink that writes directly to the file system."""

    def write(self, path: Path, content: bytes) -> None:
        """Atomically write binary content to a physical file path."""
        with atomic_write(path) as f:
            f.write(content)


class MemorySink:
    """A write sink that stores files in a dictionary."""

    def __init__(self) -> None:
        self.files: dict[str, bytes] = {}

    def write(self, path: Path, content: bytes) -> None:
        """Store the binary content in memory using the string path as a key."""
        self.files[str(path)] = content
