from dataclasses import dataclass, field


@dataclass
class ValueIR:
    value: object
    origin: dict[str, object] = field(default_factory=dict)


@dataclass
class TokenIR:
    name: str
    type_: str
    mapping: dict[str, ValueIR] = field(default_factory=dict)


@dataclass
class ArtifactIR:
    format: str
    output_path: str


@dataclass
class TargetIR:
    id: str
    tokens: dict[str, TokenIR] = field(default_factory=dict)
    artifacts: list[ArtifactIR] = field(default_factory=list)


@dataclass
class IR:
    targets: dict[str, TargetIR] = field(default_factory=dict)
