from dataclasses import InitVar, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Literal

from resforge.types import Color

ColorSpace = Literal["srgb", "display-p3"]
DisplayGamut = Literal["sRGB", "display-P3"]
Idiom = Literal["universal", "iphone", "ipad", "car", "mac", "vision", "watch", "tv"]
Subtype = Literal["mac-catalyst"]


class Appearance(Enum):
    Light = ("luminosity", "light")
    Dark = ("luminosity", "dark")
    HighContrast = ("contrast", "high")

    def __init__(self, category: str, setting: str):
        self.category = category
        self.setting = setting


@dataclass
class AppleColor:
    color: InitVar[str | Color]
    color_space: ColorSpace = "srgb"
    idiom: Idiom = "universal"
    subtype: Subtype | None = None
    appearances: List[Appearance] = field(default_factory=list)
    display_gamut: DisplayGamut | None = None

    def __post_init__(self, color: str | Color) -> None:
        self.components = color if isinstance(color, Color) else Color.from_hex(color)

    def to_dict(self) -> Dict[str, Any]:
        result: dict[str, Any] = {
            "idiom": self.idiom,
            "color": {
                "components": {
                    "red": f"{self.components.red:.3f}",
                    "green": f"{self.components.green:.3f}",
                    "blue": f"{self.components.blue:.3f}",
                    "alpha": f"{self.components.alpha:.3f}",
                },
            },
        }

        result["color"]["color-space"] = self.color_space

        if self.appearances:
            result["appearances"] = [
                {"appearance": a.category, "value": a.setting} for a in self.appearances
            ]

        if self.display_gamut is not None:
            result["display-gamut"] = self.display_gamut

        if self.subtype:
            result["subtype"] = self.subtype

        return result
