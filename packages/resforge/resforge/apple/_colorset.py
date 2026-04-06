from pathlib import Path
from typing import Any, Self, assert_never

from resforge.types import Color

from ._base import AssetNode
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

    def _create_contents(self) -> dict[str, Any]:
        self._validate()

        return {
            "info": {"author": "xcode", "version": 1},
            "colors": [color.to_dict() for color in self._colors],
        }

    def _validate(self) -> None:
        if not self._colors:
            msg = "ColorSet requires at least one color"
            raise ValueError(msg)

        variants = [frozenset(a.setting for a in c.appearances) for c in self._colors]

        seen = set()
        for v in variants:
            if v in seen:
                name = ", ".join(v) if v else "any"
                msg = f"Duplicate color appearance: [{name}]"
                raise ValueError(msg)
            seen.add(v)

        if frozenset() not in seen:
            msg = "ColorSet must have [any] appearance"
            raise ValueError(msg)

        if frozenset({"dark", "high"}) in seen and frozenset({"dark"}) not in seen:
            msg = (
                "ColorSet with [dark, high]' variant must also include a [dark] variant"
            )
            raise ValueError(msg)

        if frozenset({"light", "high"}) in seen and frozenset({"light"}) not in seen:
            msg = "ColorSet with [light, high] variant must also include a [light] variant"
            raise ValueError(msg)
