from dataclasses import dataclass, field

__all__ = ["IR", "ArtifactNode", "TargetNode", "TokenNode", "ValueNode"]


@dataclass
class ValueNode:
    value: object
    origin: dict[str, object] = field(default_factory=dict)


@dataclass
class TokenNode:
    name: str
    type_: str
    mapping: dict[str, ValueNode] = field(default_factory=dict)


@dataclass
class ArtifactNode:
    format: str
    output_path: str


@dataclass
class TargetNode:
    id: str
    tokens: dict[str, TokenNode] = field(default_factory=dict)
    artifacts: list[ArtifactNode] = field(default_factory=list)


@dataclass
class IR:
    targets: dict[str, TargetNode] = field(default_factory=dict)
