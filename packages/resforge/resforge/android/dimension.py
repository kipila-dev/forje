from typing import Any, Callable, Literal

DimensionUnit = Literal["dp", "sp", "px", "pt", "mm", "in"]


class Dimension:
    """Represents an Android dimension value (e.g., '16dp', '12sp')."""

    value: int | float
    unit: DimensionUnit

    def __init__(self, value: int | float, unit: DimensionUnit):
        """
        Args:
            value: The numeric dimension value. Negative values are permitted
                to support negative margins/offsets, though they are
                typically ignored by padding and size attributes.
            unit: The unit of measure (dp, sp, px, pt, mm, in).
        """
        self.value = value
        self.unit = unit

    def __str__(self) -> str:
        return f"{self.value:g}{self.unit}"

    def __repr__(self) -> str:
        return f"Dimension(value={self.value!r}, unit={self.unit!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Dimension):
            return NotImplemented
        return self.value == other.value and self.unit == other.unit

    def __mul__(self, other: Any) -> "Dimension":
        if not isinstance(other, (int, float)):
            return NotImplemented
        return Dimension(self.value * other, self.unit)

    def __rmul__(self, other: Any) -> "Dimension":
        return self.__mul__(other)


def _make_unit_func(
    unit: DimensionUnit, doc: str
) -> Callable[[int | float], Dimension]:
    def f(value: int | float) -> Dimension:
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
