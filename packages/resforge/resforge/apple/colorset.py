from pathlib import Path
from typing import Any, Dict, Self, assert_never

from resforge.types import Color

from .base import AssetNode
from .types import AppleColor


class ColorSet(AssetNode):
    def __init__(self, path: str | Path, name: str) -> None:
        super().__init__(path, name, "colorset")
        self._colors: list[AppleColor] = []

    def color(self, *colors: str | Color | AppleColor) -> Self:
        for c in colors:
            match c:
                case str():
                    self._colors.append(AppleColor(Color.from_hex(c)))
                case Color():
                    self._colors.append(AppleColor(c))
                case AppleColor():
                    self._colors.append(c)
                case _:
                    assert_never(c)
        return self

    def _create_contents(self) -> Dict[str, Any]:
        self._validate()

        return {
            "info": {"author": "xcode", "version": 1},
            "colors": [color.to_dict() for color in self._colors],
        }

    def _validate(self) -> None:
        if not self._colors:
            raise ValueError("ColorSet requires at least one color")

        variants = [frozenset(a.setting for a in c.appearances) for c in self._colors]

        seen = set()
        for v in variants:
            if v in seen:
                name = ", ".join(v) if v else "any"
                raise ValueError(f"Duplicate color appearance: [{name}]")
            seen.add(v)

        if frozenset() not in seen:
            raise ValueError("ColorSet must have [any] appearance")

        if frozenset({"dark", "high"}) in seen and frozenset({"dark"}) not in seen:
            raise ValueError(
                "ColorSet with [dark, high]' variant must also include a [dark] variant"
            )

        if frozenset({"light", "high"}) in seen and frozenset({"light"}) not in seen:
            raise ValueError(
                "ColorSet with [light, high] variant must also include a [light] variant"
            )
