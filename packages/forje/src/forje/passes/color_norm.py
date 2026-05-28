from typing import final, override

import coloraide

from forje.core.driver import Pass
from forje.ir import IR, TokenNode
from forje.ir.models import ColorNode

__all__ = ["ColorCanonicalizer"]


def _normalize_color_node(node: ColorNode) -> ColorNode:
    if node.space == "xyz-d65":
        return node

    match node.space:
        case "oklch" | "srgb":
            space = node.space
        case "p3":
            space = "display-p3"

    color = coloraide.Color(space, node.coords, alpha=node.alpha).convert("xyz-d65")
    coords = color.coords()

    return ColorNode(
        coords=(coords[0], coords[1], coords[2]),
        alpha=color.alpha(),
        space="xyz-d65",
    )


def _normalize_token_node(node: TokenNode) -> TokenNode:
    for mode, color in node.mapping.items():
        node.mapping[mode] = _normalize_color_node(color)
    if node.on:
        node.on = _normalize_token_node(node.on)
    return node


@final
class ColorCanonicalizer(Pass):
    """Normalizes all `ColorNode` values across all targets into xyz-d65 color space."""

    @override
    def run(self, ir: IR) -> None:
        for target in ir.targets.values():
            for name, token in target.tokens.items():
                target.tokens[name] = _normalize_token_node(token)
