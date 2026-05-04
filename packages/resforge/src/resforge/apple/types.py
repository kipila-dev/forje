from dataclasses import InitVar, dataclass, field
from enum import Enum
from typing import Any, Literal

from resforge.types import Color

ColorSpace = Literal["srgb", "display-p3"]
DisplayGamut = Literal["sRGB", "display-P3"]
Idiom = Literal["universal", "iphone", "ipad", "car", "mac", "vision", "watch", "tv"]
Subtype = Literal["mac-catalyst"]


class Appearance(Enum):
    """A color appearance variant.

    Attributes:
        Light: Standard light mode.
        Dark: Standard dark mode.
        HighContrast: High contrast mode.

    """

    Light = ("luminosity", "light")
    Dark = ("luminosity", "dark")
    HighContrast = ("contrast", "high")

    def __init__(self, category: str, setting: str) -> None:
        self.category = category
        self.setting = setting


@dataclass
class AppleColor:
    """A single color entry for an Apple asset catalog.

    Represents one color variant within a ColorSet, targeting a specific
    idiom, appearance, and display configuration.
    """

    color: InitVar[str | Color]
    components: Color = field(init=False)
    color_space: ColorSpace = "srgb"
    idiom: Idiom = "universal"
    subtype: Subtype | None = None
    appearances: list[Appearance] = field(default_factory=list)
    display_gamut: DisplayGamut | None = None

    def __post_init__(self, color: str | Color) -> None:
        self.components = Color(color)

    def to_dict(self) -> dict[str, Any]:
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
