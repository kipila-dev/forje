from typing import final, override

import coloraide

from forje.core.pass_ import Pass
from forje.ir import IR, TokenNode
from forje.ir.models import ColorNode

__all__ = ["ColorCanonicalizer", "normalize_color_node", "normalize_token_node"]


def normalize_color_node(node: ColorNode) -> ColorNode:
    """Converts a `ColorNode` to xyz-d65.

    Returns the node unchanged if it's already in xyz-d65 space.
    """
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


def normalize_token_node(node: TokenNode) -> TokenNode:
    """Normalizes all color mappings in a token to xyz-d65 in-place."""
    for mode, color in node.mapping.items():
        node.mapping[mode] = normalize_color_node(color)
    return node


@final
class ColorCanonicalizer(Pass):
    """Normalizes all `ColorNode` values across all targets into xyz-d65 color space."""

    @override
    def run(self, ir: IR) -> None:
        for target in ir.targets.values():
            for name, token in target.tokens.items():
                target.tokens[name] = normalize_token_node(token)
