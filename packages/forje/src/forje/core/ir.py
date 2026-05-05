from dataclasses import dataclass, field


@dataclass
class TargetIR:
    name: str


@dataclass
class IR:
    targets: list[TargetIR] = field(default_factory=list)
