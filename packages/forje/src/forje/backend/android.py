from pathlib import Path
from typing import final, override

from resforge import Color
from resforge.android import ValuesWriter
from resforge.io import MemorySink, WriteSink

from forje.backend import Backend
from forje.ir import ArtifactNode, TargetNode, TokenMapping
from forje.ir.models import ColorNode


def _to_color(node: ColorNode) -> Color:
    return Color(
        x=node.coords[0],
        y=node.coords[1],
        z=node.coords[2],
        alpha=node.alpha,
    )


def _write_tokens(sink: WriteSink, path: Path, nodes: dict[str, ColorNode]) -> None:
    with ValuesWriter(path, sink=sink) as res:
        colors = {name: _to_color(node) for name, node in nodes.items()}
        res.color(**colors)


@final
class Android(Backend):
    """Generates Android XML resource files for colors from design tokens."""

    @override
    def codegen(self, target: TargetNode, artifact: ArtifactNode) -> dict[str, bytes]:
        colors = [t for t in target.tokens.values() if t.kind == "color"]

        def get_mapping(mode: TokenMapping) -> dict[str, ColorNode]:
            return {t.name: t.mapping[mode] for t in colors if mode in t.mapping}

        light = get_mapping("light")
        dark = get_mapping("dark")

        sink = MemorySink()
        base_path = Path(artifact.path)
        stem = artifact.stem or "colors"

        _write_tokens(sink, base_path / "values" / f"{stem}.xml", light)
        _write_tokens(sink, base_path / "values-night" / f"{stem}.xml", dark)

        return sink.files
