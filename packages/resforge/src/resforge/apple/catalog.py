import json
import shutil
from io import BytesIO
from pathlib import Path
from typing import Self, final

from resforge._utils import require_context
from resforge.io import FileSystemSink, WriteSink

from ._colorset import ColorSet
from .types import AppleColor

__all__ = ["AssetCatalog"]


@final
class AssetCatalog:
    """A context manager for generating Apple Asset Catalogs (.xcassets).

    To ensure atomic writes, it works in a temporary directory and only swaps
    to the final destination upon successful completion of the context.

    Example:
        >>> with AssetCatalog("App", "Assets") as assets:
        ...     assets.colorset("primary", "#FF0000")
    """

    def __init__(
        self,
        path: str | Path,
        name: str,
        *,
        sink: WriteSink | None = None,
    ) -> None:
        """Initializes the AssetCatalog.

        Args:
            path: The filesystem path where the asset catalog will be saved.
            name: The name of the catalog (without .xcassets extension).
            sink: The custom output to write data to. If None,
                defaults to a standard file write.
        """
        self._active = False
        output_dir = Path(path)
        self._final_path = output_dir / f"{name}.xcassets"
        self._sink = sink or FileSystemSink()
        self._temp_path = (
            (output_dir / f".tmp_{name}.xcassets")
            if isinstance(self._sink, FileSystemSink)
            else self._final_path
        )

    def __enter__(self) -> Self:
        self._active = True
        if isinstance(self._sink, FileSystemSink):
            if self._temp_path.exists():
                shutil.rmtree(self._temp_path)
            self._temp_path.mkdir(parents=True)
        return self

    def __exit__(self, exc_type: type[BaseException] | None, *_: object) -> None:
        try:
            if exc_type is None:
                buf = BytesIO()
                contents = {"info": {"author": "xcode", "version": 1}}
                buf.write(json.dumps(contents, indent=2).encode())
                path = Path(self._temp_path) / "Contents.json"
                self._sink.write(path, buf.getvalue())
                if isinstance(self._sink, FileSystemSink):
                    if self._final_path.exists():
                        shutil.rmtree(self._final_path)
                    self._temp_path.rename(self._final_path)
        finally:
            if isinstance(self._sink, FileSystemSink) and self._temp_path.exists():
                shutil.rmtree(self._temp_path)
            self._active = False

    @require_context
    def colorset(self, name: str, *colors: AppleColor) -> Self:
        """Creates a .colorset folder within the catalog.

        Args:
            name: The name of the color resource (without .colorset extension).
            *colors: One or more AppleColor definitions.

        """
        with ColorSet(self._temp_path, name, self._sink) as colorset:
            colorset.color(*colors)
        return self
