from dataclasses import dataclass, field
from typing import Literal

OutputKind = Literal["android_xml", "android_compose", "apple"]


@dataclass
class OutputConfig:
    kind: OutputKind
    path: str
    package: str | None


@dataclass
class ColorIR:
    name: str
    light: str
    dark: str | None
    high_contrast_light: str | None
    high_contrast_dark: str | None


@dataclass
class ThemeIR:
    colors: list[ColorIR] = field(default_factory=list)


@dataclass
class TargetIR:
    name: str
    theme: ThemeIR
    outputs: list[OutputConfig] = field(default_factory=list)


@dataclass
class IR:
    targets: list[TargetIR] = field(default_factory=list)
