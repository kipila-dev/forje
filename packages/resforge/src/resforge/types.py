from __future__ import annotations

import re
from typing import Self, cast

__all__ = ["Color"]

_HEX_COLOR_RE = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})")


def _parse_hex(value: str) -> tuple[float, float, float, float]:
    if not _HEX_COLOR_RE.fullmatch(value):
        msg = f"Invalid hex color: {value!r}"
        raise ValueError(msg)

    hex_str = value[1:]

    if len(hex_str) in (3, 4):
        hex_str = "".join(c * 2 for c in hex_str)

    if len(hex_str) == 6:
        hex_str = "FF" + hex_str

    a, r, g, b = bytes.fromhex(hex_str)

    return a / 255, r / 255, g / 255, b / 255


class Color:
    """Represents an ARGB color, constructed from a hex string.

    Accepts #RGB, #ARGB, #RRGGBB, or #AARRGGBB formats.
    """

    __slots__ = ("alpha", "blue", "green", "red")

    def __new__(cls, value: str | Color) -> Self:
        if isinstance(value, Color):
            return cast("Self", value)
        return super().__new__(cls)

    def __init__(self, value: str | Color) -> None:
        if isinstance(value, Color):
            return
        a, r, g, b = _parse_hex(value)
        self.red = r
        self.green = g
        self.blue = b
        self.alpha = a

    @property
    def hex(self) -> str:
        """Returns the color as a #AARRGGBB string."""
        a = round(self.alpha * 255)
        r = round(self.red * 255)
        g = round(self.green * 255)
        b = round(self.blue * 255)
        return f"#{a:02X}{r:02X}{g:02X}{b:02X}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Color):
            return NotImplemented
        return (self.red, self.green, self.blue, self.alpha) == (
            other.red,
            other.green,
            other.blue,
            other.alpha,
        )

    def __hash__(self) -> int:
        return hash((self.red, self.green, self.blue, self.alpha))

    def __repr__(self) -> str:
        return f"Color({self.hex!r})"
