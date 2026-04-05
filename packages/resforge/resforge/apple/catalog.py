import shutil
from pathlib import Path
from typing import Self

from resforge._utils import require_context
from resforge.types import Color

from .base import write_contents
from .colorset import ColorSet
from .types import AppleColor

__all__ = ["AssetCatalog"]


class AssetCatalog:
    """
    A fluent context manager for generating Apple Asset Catalogs (.xcassets).

    To ensure atomic writes, it works in a temporary directory and only swaps
    to the final destination upon successful completion of the context.

    Example:
        >>> with AssetCatalog("App", "Assets") as assets:
        ...     assets.colorset("primary", "#FF0000")
    """

    def __init__(self, path: str | Path, name: str) -> None:
        """
        Args:
            path: The filesystem path where the asset catalog will be saved.
            name: The name of the catalog (without .xcassets extension).
        """
        output_dir = Path(path).resolve()
        self._temp_path = output_dir / f".tmp_{name}.xcassets"
        self._final_path = output_dir / f"{name}.xcassets"
        self._active = False

    def __enter__(self) -> Self:
        self._active = True
        if self._temp_path.exists():
            shutil.rmtree(self._temp_path)
        self._temp_path.mkdir(parents=True)
        return self

    def __exit__(self, exc_type, *_) -> None:
        self._active = False
        try:
            if exc_type is None:
                contents = {"info": {"author": "xcode", "version": 1}}
                write_contents(self._temp_path, contents)
                if self._final_path.exists():
                    shutil.rmtree(self._final_path)
                self._temp_path.rename(self._final_path)
        finally:
            if self._temp_path.exists():
                shutil.rmtree(self._temp_path)

    @require_context
    def colorset(self, name: str, *colors: str | Color | AppleColor) -> Self:
        """
        Creates a .colorset folder within the catalog.

        Args:
            name: The name of the color resource (without .colorset extension).
            *colors: One or more color definitions. Accepts hex strings,
                Color objects, or AppleColor objects for platform-specific specs.
        """
        with ColorSet(self._temp_path, name) as cs:
            cs.color(*colors)
        return self
