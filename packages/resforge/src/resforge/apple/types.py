from __future__ import annotations

import typing
from dataclasses import InitVar, dataclass, field
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

    @property
    def category(self) -> str:
        return self.value[0]

    @property
    def setting(self) -> str:
        return self.value[1]


@dataclass
class AppleColor:
    """A single color entry for an Apple asset catalog."""

    _color: InitVar[str | Color]
    color: Color = field(init=False)
    idiom: Idiom = "universal"
    subtype: Subtype | None = None
    appearances: list[Appearance] = field(default_factory=list)

    def __post_init__(self, color: str | Color) -> None:
        self.color = Color.parse(color)

    def to_entries(self) -> list[dict[str, typing.Any]]:
        """Serialize this color into one or two asset catalog entries.

        Always produces an sRGB entry. For wide-gamut colors that fall outside
        the sRGB gamut, also produces a Display P3 entry so devices without a
        P3 display receive a correct fallback.
        """
        srgb = self._entry(self.color.to_srgb_components(), "srgb")
        entries = [srgb]
        if not self.color.in_srgb_gamut():
            p3 = self._entry(self.color.to_p3_components(), "display-p3", "display-P3")
            entries.append(p3)
        return entries

    def _entry(
        self,
        components: tuple[float, float, float, float],
        space: ColorSpace,
        gamut: DisplayGamut | None = None,
    ) -> dict[str, typing.Any]:
        entry: dict[str, typing.Any] = {
            "idiom": self.idiom,
            "color": {
                "components": {
                    "red": f"{components[0]:.3f}",
                    "green": f"{components[1]:.3f}",
                    "blue": f"{components[2]:.3f}",
                    "alpha": f"{components[3]:.3f}",
                },
                "color-space": space,
            },
        }

        if self.appearances:
            entry["appearances"] = [
                {"appearance": a.category, "value": a.setting} for a in self.appearances
            ]

        if gamut is not None:
            entry["display-gamut"] = gamut

        if self.subtype:
            entry["subtype"] = self.subtype

        return entry
