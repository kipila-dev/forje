import math
from pathlib import Path
from typing import final, override

from resforge import Color
from resforge.io import MemorySink

from forje.backend import Backend
from forje.ir import ArtifactNode, ColorNode, TargetNode, TokenMapping

__all__ = ["CSS"]

_QUERY_CONTRAST = "(prefers-contrast: more)"
_QUERY_LIGHT = "(prefers-color-scheme: light)"
_QUERY_DARK = "(prefers-color-scheme: dark)"
_QUERIES: dict[TokenMapping, str | None] = {
    "light": None,
    "dark": f"@media {_QUERY_DARK}",
    "high_contrast_light": f"@media {_QUERY_CONTRAST} and {_QUERY_LIGHT}",
    "high_contrast_dark": f"@media {_QUERY_CONTRAST} and {_QUERY_DARK}",
}


def _to_color(node: ColorNode) -> Color:
    return Color(
        x=node.coords[0],
        y=node.coords[1],
        z=node.coords[2],
        alpha=node.alpha,
    )


def _to_css_vars(name: str, node: ColorNode) -> tuple[str, str]:
    name = f"--color-{name.lower().strip().replace('_', '-')}"
    color = _to_color(node)

    r, g, b, a_srgb = color.to_srgb_components()
    r = round(r * 255)
    g = round(g * 255)
    b = round(b * 255)

    l, c, h, a_oklch = color.to_oklch_components()
    h = "none" if math.isnan(h) else round(h, 3)

    return (
        f"{name}: rgb({r} {g} {b} / {a_srgb:.3f});",
        f"{name}: oklch({l:.3f} {c:.3f} {h} / {a_oklch:.3f});",
    )


def _add_indent(lines: list[str], level: int = 1) -> list[str]:
    return [f"{'  ' * level}{l}" for l in lines]


def _to_css_block(vars_: list[str], query: str | None = None) -> str:
    query = (query or "").strip()

    block = [":root {", *_add_indent(vars_), "}"]

    if query:
        block = [f"{query} {{", *_add_indent(block), "}"]

    return "\n".join(block)


@final
class CSS(Backend):
    """Generates CSS custom properties from design tokens."""

    @override
    def codegen(self, target: TargetNode, artifact: ArtifactNode) -> dict[str, bytes]:
        vars_: dict[TokenMapping, list[str]] = {
            "light": [],
            "dark": [],
            "high_contrast_light": [],
            "high_contrast_dark": [],
        }

        color_tokens = (t for t in target.tokens.values() if t.kind == "color")

        for token in color_tokens:
            for mode, node in token.mapping.items():
                vars_[mode].extend(v for v in _to_css_vars(token.name, node))

        blocks: list[str] = [
            _to_css_block(v, _QUERIES[m]) for m, v in vars_.items() if v
        ]

        css = "\n\n".join(blocks) + "\n"

        sink = MemorySink()
        sink.write(
            Path(artifact.path) / f"{artifact.stem or 'tokens'}.css",
            css.encode(),
        )
        return sink.files
