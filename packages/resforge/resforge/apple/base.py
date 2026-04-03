import json
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Self


def write_contents(path: str | Path, contents: Dict[str, Any]) -> None:
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
            write_contents(self._path, contents)
        else:
            if self._path.exists():
                shutil.rmtree(self._path)

    @abstractmethod
    def _create_contents(self) -> Dict[str, Any]: ...
