import typing
from pathlib import Path

from resforge import Color
from resforge.android import ValuesWriter
from resforge.io import MemorySink

from forje.backend import Backend
from forje.ir import ArtifactNode, TargetNode, ValueNode


def _parse_color(value: dict[str, typing.Any]) -> Color | None:
    coords = value["coords"]
    if value["space"] == "srgb":
        return Color.srgb(r=coords[0], g=coords[1], b=coords[2], alpha=value["alpha"])
    if value["space"] == "p3":
        return Color.p3(r=coords[0], g=coords[1], b=coords[2], alpha=value["alpha"])
    return None


class Android(Backend):
    def _write_tokens(
        self,
        sink: MemorySink,
        path: Path,
        nodes: list[tuple[str, ValueNode]],
    ):
        colors = {name: _parse_color(node.value) for name, node in nodes}
        with ValuesWriter(path, sink) as res:
            res.color(**colors)

    def codegen(self, target: TargetNode, artifact: ArtifactNode) -> dict[str, bytes]:
        colors = [token for token in target.tokens.values() if token.type_ == "color"]
        light = [
            (token.name, token.mapping["light"])
            for token in colors
            if "light" in token.mapping
        ]
        dark = [
            (token.name, token.mapping["dark"])
            for token in colors
            if "dark" in token.mapping
        ]

        base_path = Path(artifact.path)
        stem = artifact.stem or "colors"
        sink = MemorySink()

        self._write_tokens(sink, base_path / "values" / f"{stem}.xml", light)
        self._write_tokens(sink, base_path / "values-night" / f"{stem}.xml", dark)

        return sink.files
