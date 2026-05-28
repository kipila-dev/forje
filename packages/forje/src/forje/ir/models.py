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
    "TokenNode",
]


ColorSpace = Literal["oklch", "p3", "srgb", "xyz-d65"]
TokenKind = Literal["color"]


@dataclass
class ColorNode:
    coords: tuple[float, float, float]
    alpha: float = 1.0
    space: ColorSpace = "srgb"


@dataclass
class TokenNode:
    name: str
    kind: TokenKind
    on: TokenNode | None = None
    mapping: dict[str, ColorNode] = Field(default_factory=dict)


@dataclass
class ArtifactNode:
    platform: str
    path: str
    stem: str | None = None


@dataclass
class TargetNode:
    id: str
    tokens: dict[str, TokenNode] = Field(default_factory=dict)
    artifacts: list[ArtifactNode] = Field(default_factory=list)


@dataclass
class IR:
    targets: dict[str, TargetNode] = Field(default_factory=dict)
    outputs: dict[str, dict[str, dict[str, bytes]]] = Field(default_factory=dict)
