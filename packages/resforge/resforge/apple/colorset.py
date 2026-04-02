from pathlib import Path
from typing import Any, Dict, assert_never

from resforge.types import Color

from .catalog import AssetNode
from .types import AppleColor


class ColorSet(AssetNode):
    def __init__(self, path: str | Path, name: str) -> None:
        super().__init__(path, name, "colorset")
        self._colors: list[AppleColor] = []

    def color(self, *colors: str | Color | AppleColor) -> None:
        for c in colors:
            match c:
                case str():
                    self._colors.append(AppleColor(components=Color.from_hex(c)))
                case Color():
                    self._colors.append(AppleColor(components=c))
                case AppleColor():
                    self._colors.append(c)
                case _:
                    assert_never(c)

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
