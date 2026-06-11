from __future__ import annotations

from typing import Literal

from pydantic import Field
from pydantic.dataclasses import dataclass

__all__ = [
    "IR",
    "ArtifactNode",
    "ColorNode",
    "ColorSpace",
    "TargetNode",
    "TokenMapping",
    "TokenNode",
]


ColorSpace = Literal["oklch", "p3", "srgb", "xyz-d65"]
TokenKind = Literal["color"]
TokenMapping = Literal["dark", "light", "high_contrast_dark", "high_contrast_light"]


@dataclass
class ColorNode:
    """A color value in a specific color space."""

    coords: tuple[float, float, float]
    alpha: float = 1.0
    space: ColorSpace = "srgb"


@dataclass
class TokenNode:
    """A named design token with one or more appearance-mapped colors."""

    name: str
    kind: TokenKind
    context: list[object]
    mapping: dict[TokenMapping, ColorNode] = Field(default_factory=dict)


@dataclass
class ArtifactNode:
    """Output configuration for a single platform."""

    platform: str
    path: str
    stem: str | None = None


@dataclass
class TargetNode:
    """A named build target grouping tokens and artifact configs."""

    id: str
    tokens: dict[str, TokenNode] = Field(default_factory=dict)
    artifacts: list[ArtifactNode] = Field(default_factory=list)


@dataclass
class IR:
    """The intermediate representation of a parsed build script."""

    targets: dict[str, TargetNode] = Field(default_factory=dict)
    outputs: dict[str, dict[str, dict[str, bytes]]] = Field(default_factory=dict)
