import json
import shutil
import typing
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Self

from resforge._utils import atomic_write


def write_contents(path: str | Path, contents: dict[str, typing.Any]) -> None:
    path = Path(path) / "Contents.json"
    with atomic_write(path) as tf:
        tf.write(json.dumps(contents, indent=2).encode())


class AssetNode(ABC):
    def __init__(self, path: str | Path, name: str, extension: str) -> None:
        self._path: Path = Path(path) / f"{name}.{extension}"

    def __enter__(self) -> Self:
        self._path.mkdir(parents=True, exist_ok=True)
        return self

    def __exit__(self, exc_type: type[BaseException] | None, *_: object) -> None:
        if exc_type is None:
            contents = self._create_contents()
            write_contents(self._path, contents)
        elif self._path.exists():
            shutil.rmtree(self._path)

    @abstractmethod
    def _create_contents(self) -> dict[str, object]: ...
