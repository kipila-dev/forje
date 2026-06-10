from __future__ import annotations

from dataclasses import dataclass

import coloraide

__all__ = ["Color"]


@dataclass(slots=True, frozen=True)
class Color:
    """A representation of a color, stored internally in the CIE XYZ color space."""

    x: float
    y: float
    z: float
    alpha: float = 1.0

    def __post_init__(self) -> None:
        if not (0 <= self.alpha <= 1):
            msg = "Alpha must be in [0.0, 1.0]"
            raise ValueError(msg)

    @classmethod
    def _to_xyz(cls, color: coloraide.Color) -> Color:
        xyz = color.convert("xyz-d65")
        return cls(x=xyz["x"], y=xyz["y"], z=xyz["z"], alpha=xyz.alpha())

    @classmethod
    def parse(cls, value: str | Color) -> Color:
        """Create a Color instance from a string or another Color object."""
        match value:
            case str():
                try:
                    color = coloraide.Color(value)
                except Exception as e:
                    msg = f"Invalid value: {value!r}"
                    raise ValueError(msg) from e
                return cls._to_xyz(color)
            case Color():
                return value

    @classmethod
    def srgb(cls, r: float, g: float, b: float, alpha: float = 1.0) -> Color:
        """Create a Color instance from sRGB components."""
        if not (0 <= r <= 1 and 0 <= g <= 1 and 0 <= b <= 1):
            msg = "sRGB components must be in [0.0, 1.0]"
            raise ValueError(msg)
        if not (0 <= alpha <= 1):
            msg = "Alpha must be in [0.0, 1.0]"
            raise ValueError(msg)
        color = coloraide.Color("srgb", [r, g, b], alpha)
        return cls._to_xyz(color)

    @classmethod
    def p3(cls, r: float, g: float, b: float, alpha: float = 1.0) -> Color:
        """Create a Color instance from Display P3 components."""
        if not (0 <= r <= 1 and 0 <= g <= 1 and 0 <= b <= 1):
            msg = "Display P3 components must be in [0.0, 1.0]"
            raise ValueError(msg)
        if not (0 <= alpha <= 1):
            msg = "Alpha must be in [0.0, 1.0]"
            raise ValueError(msg)
        color = coloraide.Color("display-p3", [r, g, b], alpha)
        return cls._to_xyz(color)

    @classmethod
    def oklch(cls, l: float, c: float, h: float, alpha: float = 1.0) -> Color:
        """Create a Color instance from OKLCh components."""
        if not (0 <= l <= 1):
            msg = "OKLCh lightness must be in [0.0, 1.0]"
            raise ValueError(msg)
        if c < 0:
            msg = "OKLCh chroma must be non-negative"
            raise ValueError(msg)
        if not (0 <= alpha <= 1):
            msg = "Alpha must be in [0.0, 1.0]"
            raise ValueError(msg)
        color = coloraide.Color("oklch", [l, c, h], alpha)
        return cls._to_xyz(color)

    def _to_coloraide(self) -> coloraide.Color:
        return coloraide.Color("xyz-d65", [self.x, self.y, self.z], self.alpha)

    def to_srgb_components(self) -> tuple[float, float, float, float]:
        """Convert the color to sRGB components (R, G, B, A).

        Colors outside sRGB gamut are automatically clipped to the nearest valid
        boundary.
        """
        srgb = self._to_coloraide().convert("srgb").clip()
        return (
            round(srgb["red"], 3) + 0.0,
            round(srgb["green"], 3) + 0.0,
            round(srgb["blue"], 3) + 0.0,
            round(self.alpha, 3) + 0.0,
        )

    def to_p3_components(self) -> tuple[float, float, float, float]:
        """Convert the color to Display P3 components (R, G, B, A).

        Colors outside Display P3 gamut are automatically clipped to the nearest
        valid boundary.
        """
        p3 = self._to_coloraide().convert("display-p3").clip()
        return (
            round(p3["red"], 3) + 0.0,
            round(p3["green"], 3) + 0.0,
            round(p3["blue"], 3) + 0.0,
            round(self.alpha, 3) + 0.0,
        )

    def to_srgb_argb_hex(self, prefix: str = "#") -> str:
        """Convert the color to an ARGB hexadecimal string.

        Colors outside sRGB gamut are automatically clipped to the nearest valid
        boundary.
        """
        srgb = self._to_coloraide().convert("srgb").clip()
        a = round(self.alpha * 255)
        r = round(srgb["red"] * 255)
        g = round(srgb["green"] * 255)
        b = round(srgb["blue"] * 255)
        return f"{prefix}{a:02X}{r:02X}{g:02X}{b:02X}"

    def in_srgb_gamut(self) -> bool:
        """Check if the color is representable in the sRGB color space."""
        return self._to_coloraide().in_gamut("srgb")
