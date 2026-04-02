import re
from dataclasses import dataclass
from typing import Self

__all__ = ["Color"]

_HEX_COLOR_RE = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})")


def _parse_hex(value: str) -> tuple[float, float, float, float]:
    if not _HEX_COLOR_RE.fullmatch(value):
        raise ValueError(f"Invalid hex color: {value!r}")

    hex_str = value[1:]

    if len(hex_str) in (3, 4):
        hex_str = "".join(c * 2 for c in hex_str)

    if len(hex_str) == 6:
        hex_str = "FF" + hex_str

    a, r, g, b = bytes.fromhex(hex_str)

    return a / 255, r / 255, g / 255, b / 255


@dataclass(frozen=True)
class Color:
    """
    Represents a color using float components (0.0 to 1.0).
    """

    red: float
    green: float
    blue: float
    alpha: float = 1.0

    def __post_init__(self) -> None:
        for field in (self.red, self.green, self.blue, self.alpha):
            if not 0.0 <= field <= 1.0:
                raise ValueError(
                    f"Color components must be between 0 and 1 (got {field})"
                )

    @classmethod
    def from_hex(cls, value: str) -> Self:
        """Accepts #RGB, #ARGB, #RRGGBB, or #AARRGGBB."""
        a, r, g, b = _parse_hex(value)
        return cls(red=r, green=g, blue=b, alpha=a)

    @property
    def to_hex(self) -> str:
        """Returns the color as a #AARRGGBB string."""
        a = round(self.alpha * 255)
        r = round(self.red * 255)
        g = round(self.green * 255)
        b = round(self.blue * 255)
        return f"#{a:02x}{r:02x}{g:02x}{b:02x}".upper()
