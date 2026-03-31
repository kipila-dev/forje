from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Literal

from .catalog import AssetNode
from .types import ColorSpace, DisplayGamut, Idiom


@dataclass
class Color:
    red: float
    green: float
    blue: float
    alpha: float = 1.0
    color_space: ColorSpace | None = None
    appearance: Literal["light", "dark"] | None = None
    display_gamut: DisplayGamut | None = None
    idiom: Idiom = "universal"

    def __post_init__(self) -> None:
        for field in (self.red, self.green, self.blue, self.alpha):
            if not 0.0 <= field <= 1.0:
                raise ValueError(
                    f"Color components must be between 0 and 1 (got {field})"
                )

    def to_dict(self) -> Dict[str, Any]:
        result: dict[str, Any] = {
            "color": {
                "components": {
                    "red": self.red,
                    "green": self.green,
                    "blue": self.blue,
                    "alpha": self.alpha,
                },
            }
        }

        if self.color_space is not None:
            result["color"]["color-space"] = self.color_space

        if self.appearance is not None:
            result["appearances"] = [
                {"appearance": "luminosity", "value": self.appearance}
            ]

        if self.display_gamut is not None:
            result["display-gamut"] = self.display_gamut

        if self.idiom is not None:
            result["idiom"] = self.idiom

        return result


class ColorSet(AssetNode):
    def __init__(self, path: str | Path, name: str) -> None:
        super().__init__(path, name, "colorset")
        self._colors: list[Color] = []

    def color(self, *color: Color) -> None:
        self._colors.extend(color)

    def _create_contents(self) -> Dict[str, Any]:
        if not self._colors:
            raise ValueError("ColorSet requires at least one color")

        appearances = {c.appearance for c in self._colors}

        if "dark" in appearances and appearances.isdisjoint({None, "light"}):
            raise ValueError("ColorSet with a dark color requires a light color")

        return {
            "info": {"author": "xcode", "version": 1},
            "colors": [color.to_dict() for color in self._colors],
        }
