from dataclasses import dataclass
from typing import Any, Dict, Literal

from resforge.types import Color

ColorSpace = Literal["srgb", "display-p3"]
DisplayGamut = Literal["sRGB", "display-P3"]
Idiom = Literal[
    "appLauncher",
    "companionSettings",
    "ios-marketing",
    "iphone",
    "ipad",
    "mac",
    "notificationCenter",
    "quickLook",
    "tv",
    "universal",
    "watch",
    "watch-marketing",
]


@dataclass
class AppleColor:
    components: Color
    color_space: ColorSpace | None = None
    appearance: Literal["light", "dark"] | None = None
    display_gamut: DisplayGamut | None = None
    idiom: Idiom = "universal"

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

        if self.color_space is not None:
            result["color"]["color-space"] = self.color_space

        if self.appearance is not None:
            result["appearances"] = [
                {"appearance": "luminosity", "value": self.appearance}
            ]

        if self.display_gamut is not None:
            result["display-gamut"] = self.display_gamut

        return result
