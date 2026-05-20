from __future__ import annotations

import typing
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal

from resforge import Color

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

    components: tuple[float, float, float, float]
    color_space: ColorSpace = "srgb"
    idiom: Idiom = "universal"
    subtype: Subtype | None = None
    appearances: list[Appearance] = field(default_factory=list)
    display_gamut: DisplayGamut | None = None

    def to_dict(self) -> dict[str, typing.Any]:
        result: dict[str, typing.Any] = {
            "idiom": self.idiom,
            "color": {
                "components": {
                    "red": f"{self.components[0]:.3f}",
                    "green": f"{self.components[1]:.3f}",
                    "blue": f"{self.components[2]:.3f}",
                    "alpha": f"{self.components[3]:.3f}",
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

    @classmethod
    def create(
        cls,
        color: str | Color,
        subtype: Subtype | None = None,
        appearances: list[Appearance] | None = None,
    ) -> list[AppleColor]:
        if appearances is None:
            appearances = []
        apple_colors: list[AppleColor] = []
        color = Color.parse(color)
        apple_colors.append(
            cls(
                components=color.to_srgb_components(),
                color_space="srgb",
                idiom="universal",
                subtype=subtype,
                appearances=appearances,
            ),
        )
        if not color.in_srgb_gamut():
            apple_colors.append(
                cls(
                    components=color.to_p3_components(),
                    color_space="display-p3",
                    idiom="universal",
                    subtype=subtype,
                    appearances=appearances,
                    display_gamut="display-P3",
                ),
            )
        return apple_colors
