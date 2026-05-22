import json
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from typing import Self

from resforge.io import WriteSink


class AssetNode(ABC):
    def __init__(
        self,
        path: str | Path,
        name: str,
        extension: str,
        sink: WriteSink,
    ) -> None:
        self._path: Path = Path(path) / f"{name}.{extension}"
        self._sink: WriteSink = sink

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: type[BaseException] | None, *_: object) -> None:
        if exc_type is None:
            contents = self._create_contents()
            buf = BytesIO()
            buf.write(json.dumps(contents, indent=2).encode())
            path = Path(self._path) / "Contents.json"
            self._sink.write(path, buf.getvalue())

    @abstractmethod
    def _create_contents(self) -> dict[str, object]: ...
