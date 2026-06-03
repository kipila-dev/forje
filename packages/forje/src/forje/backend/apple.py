import re
from typing import override

from resforge import Color
from resforge.apple import Appearance, AppleColor, AssetCatalog
from resforge.io import MemorySink

from forje.backend import Backend
from forje.ir import ArtifactNode, ColorNode, TargetNode, TokenMapping

_APPEARANCE_MAP: dict[TokenMapping, list[Appearance]] = {
    "light": [],
    "dark": [Appearance.Dark],
    "high_contrast_light": [Appearance.HighContrast, Appearance.Light],
    "high_contrast_dark": [Appearance.HighContrast, Appearance.Dark],
}


def _to_pascal_case(value: str) -> str:
    words = re.split(r"[-_]+", value)
    return "".join(w.capitalize() for w in words if w)


def _to_color(node: ColorNode) -> Color:
    return Color(
        x=node.coords[0],
        y=node.coords[1],
        z=node.coords[2],
        alpha=node.alpha,
    )


class Apple(Backend):
    @override
    def codegen(self, target: TargetNode, artifact: ArtifactNode) -> dict[str, bytes]:
        color_tokens = (t for t in target.tokens.values() if t.kind == "color")
        sink = MemorySink()

        with AssetCatalog(
            artifact.path,
            artifact.stem or "Assets",
            sink=sink,
        ) as catalog:
            for token in color_tokens:
                name = _to_pascal_case(token.name)
                apple_colors = [
                    AppleColor(_to_color(node), appearances=_APPEARANCE_MAP[mapping])
                    for mapping, node in token.mapping.items()
                ]
                catalog.colorset(name, *apple_colors)

        return sink.files
