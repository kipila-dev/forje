from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

DimensionUnit = Literal["dp", "sp", "px", "pt", "mm", "in"]


@dataclass(frozen=True)
class Dimension:
    """Represents an Android dimension value (e.g., '16dp', '12sp').

    Args:
        value: The numeric dimension value. Negative values are permitted
            to support negative margins/offsets, though they are
            typically ignored by padding and size attributes.
        unit: The unit of measure (dp, sp, px, pt, mm, in).

    """

    value: int | float
    unit: DimensionUnit

    def __str__(self) -> str:
        return f"{self.value:g}{self.unit}"

    def __repr__(self) -> str:
        return f"Dimension(value={self.value!r}, unit={self.unit!r})"

    def __mul__(self, other: float) -> "Dimension":
        return Dimension(self.value * other, self.unit)

    __rmul__ = __mul__


def _make_unit_func(
    unit: DimensionUnit, doc: str
) -> Callable[[int | float], Dimension]:
    def f(value: float) -> Dimension:
        return Dimension(value, unit)

    f.__name__ = unit
    f.__doc__ = doc
    return f


dp = _make_unit_func("dp", "Create a dimension in density-independent pixels (dp).")
sp = _make_unit_func(
    "sp", "Create a dimension in scale-independent pixels (sp). Use for text sizes."
)
px = _make_unit_func("px", "Create a dimension in pixels (px).")
pt = _make_unit_func("pt", "Create a dimension in points (pt).")
mm = _make_unit_func("mm", "Create a dimension in millimeters (mm).")
inch = _make_unit_func("in", "Create a dimension in inches (in).")
