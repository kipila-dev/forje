from pathlib import Path
from typing import Self, override

from ._base import AssetNode
from .types import AppleColor


class ColorSet(AssetNode):
    def __init__(self, path: str | Path, name: str) -> None:
        super().__init__(path, name, "colorset")
        self._colors: list[AppleColor] = []

    def color(self, *colors: AppleColor) -> Self:
        self._colors.extend(colors)
        return self

    @override
    def _create_contents(self) -> dict[str, object]:
        self._validate()

        return {
            "info": {"author": "xcode", "version": 1},
            "colors": [entry for color in self._colors for entry in color.to_entries()],
        }

    def _validate(self) -> None:
        if not self._colors:
            msg = "ColorSet requires at least one color"
            raise ValueError(msg)

        variants = [frozenset(a.setting for a in c.appearances) for c in self._colors]

        seen: set[frozenset[str]] = set()
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
                "ColorSet with [dark, high] variant must also include a [dark] variant"
            )
            raise ValueError(msg)

        if frozenset({"light", "high"}) in seen and frozenset({"light"}) not in seen:
            msg = (
                "ColorSet with [light, high] variant "
                "must also include a [light] variant"
            )
            raise ValueError(msg)
