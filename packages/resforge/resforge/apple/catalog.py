import json
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Self

from .colorset import Color, ColorSet


def _write_contents(path: str | Path, contents: Dict[str, Any]) -> None:
    path = Path(path)
    with open(path / "Contents.json", "w") as f:
        json.dump(contents, f, indent=2)


class AssetNode(ABC):
    def __init__(self, path: str | Path, name: str, extension: str) -> None:
        self._path = Path(path) / f"{name}.{extension}"

    def __enter__(self) -> Self:
        self._path.mkdir(parents=True, exist_ok=True)
        return self

    def __exit__(self, exc_type, *_) -> None:
        if exc_type is None:
            contents = self._create_contents()
            _write_contents(self._path, contents)
        else:
            if self._path.exists():
                shutil.rmtree(self._path)

    @abstractmethod
    def _create_contents(self) -> Dict[str, Any]: ...


class AssetCatalog:
    def __init__(self, path: str | Path, name: str) -> None:
        output_dir = Path(path).resolve()
        self._temp_path = output_dir / f".tmp_{name}.xcassets"
        self._final_path = output_dir / f"{name}.xcassets"

    def __enter__(self) -> Self:
        if self._temp_path.exists():
            shutil.rmtree(self._temp_path)
        self._temp_path.mkdir(parents=True)
        return self

    def __exit__(self, exc_type, *_) -> None:
        try:
            if exc_type is None:
                contents = {"info": {"author": "xcode", "version": 1}}
                _write_contents(self._temp_path, contents)
                if self._final_path.exists():
                    shutil.rmtree(self._final_path)
                self._temp_path.rename(self._final_path)
        finally:
            if self._temp_path.exists():
                shutil.rmtree(self._temp_path)

    def appiconset(self, name: str) -> Self:
        return self

    def arimageset(self, name: str) -> Self:
        return self

    def arresourcegroup(self, name: str) -> Self:
        return self

    def brandassets(self, name: str) -> Self:
        return self

    def cubetextureset(self, name: str) -> Self:
        return self

    def dataset(self, name: str) -> Self:
        return self

    def gcdashboardimage(self, name: str) -> Self:
        return self

    def gcleaderboard(self, name: str) -> Self:
        return self

    def gcleaderboardset(self, name: str) -> Self:
        return self

    def group(self, name: str) -> Self:
        return self

    def iconset(self, name: str) -> Self:
        return self

    def imageset(self, name: str) -> Self:
        return self

    def imagestack(self, name: str) -> Self:
        return self

    def imagestacklayer(self, name: str) -> Self:
        return self

    def launchimage(self, name: str) -> Self:
        return self

    def mipmapset(self, name: str) -> Self:
        return self

    def colorset(self, name: str, *color: Color) -> Self:
        with ColorSet(self._temp_path, name) as cs:
            cs.color(*color)
        return self

    def spriteatlas(self, name: str) -> Self:
        return self

    def sticker(self, name: str) -> Self:
        return self

    def stickerpack(self, name: str) -> Self:
        return self

    def stickersequence(self, name: str) -> Self:
        return self

    def textureset(self, name: str) -> Self:
        return self

    def complicationset(self, name: str) -> Self:
        return self
