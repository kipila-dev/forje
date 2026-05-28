from pathlib import Path

from resforge import Color
from resforge.android import ValuesWriter
from resforge.io import MemorySink

from forje.ir import ArtifactNode, TargetNode
from forje.ir.models import ColorNode


class Android:
    def _write_tokens(
        self,
        sink: MemorySink,
        path: Path,
        nodes: list[tuple[str, ColorNode]],
    ) -> None:
        colors = {
            name: Color(
                x=node.coords[0],
                y=node.coords[1],
                z=node.coords[2],
                alpha=node.alpha,
            )
            for name, node in nodes
        }
        with ValuesWriter(path, sink) as res:
            res.color(**colors)

    def codegen(self, target: TargetNode, artifact: ArtifactNode) -> dict[str, bytes]:
        colors = [token for token in target.tokens.values() if token.kind == "color"]
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
