import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Pattern, Self

from .dimension import Dimension
from .plural import PluralValues

_NAME_PATTERN = re.compile(r"^[a-z_][a-z0-9_]*$")
_STYLE_NAME_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_\.]*$")
_COLOR_PATTERN = re.compile(
    r"^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{4}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$"
)


class ValuesWriter:
    """
    A fluent context manager for generating Android XML resource files.

    Provides a type-safe interface for creating strings, dimensions, colors,
    and arrays. Validates resource names and color formats at runtime.

    Example:
        >>> with ValuesWriter("res/values/my_values.xml") as res:
        ...     res.dimension(padding_small=dp(8)).color(primary=0xFF0000)
    """

    def __init__(self, path: str | Path) -> None:
        """
        Args:
            path: The filesystem path where the XML will be saved.
        """
        self._path = Path(path)
        self._root: ET.Element | None = None
        self._seen_names: dict[str, set[str]] = {}

    def __enter__(self) -> Self:
        self._root = ET.Element("resources")
        self._seen_names = {}
        return self

    def __exit__(self, exc_type, *_) -> None:
        try:
            if exc_type is None and self._root is not None:
                self._path.parent.mkdir(parents=True, exist_ok=True)

                ET.indent(self._root, space="    ", level=0)

                tree = ET.ElementTree(self._root)
                tree.write(
                    self._path,
                    encoding="utf-8",
                    xml_declaration=True,
                    short_empty_elements=True,
                )
        finally:
            self._root = None
            self._seen_names.clear()

    def _prepare_text(self, text: str) -> str:
        text = text.replace("'", r"\'")
        text = text.replace('"', r"\"")
        text = text.replace("\n", r"\n")
        if text.startswith(("@", "?")):
            text = "\\" + text
        return text

    def _append(
        self,
        tag: str,
        name: str,
        text: str | None = None,
        attrs: dict[str, str] | None = None,
        name_validation_pattern: Pattern[str] = _NAME_PATTERN,
    ) -> ET.Element:
        if self._root is None:
            raise RuntimeError("ValuesWriter must be used as a context manager.")

        if not name_validation_pattern.match(name):
            raise ValueError(f"Invalid resource name '{name}'.")

        seen_for_tag = self._seen_names.setdefault(tag, set())
        if name in seen_for_tag:
            raise ValueError(
                f"Duplicate resource name '{name}' for tag <{tag}>. "
                f"The name '{name}' has already been defined with this type."
            )
        seen_for_tag.add(name)

        all_attrs = {"name": name}
        if attrs:
            all_attrs.update(attrs)
        elem = ET.SubElement(self._root, tag, attrib=all_attrs)
        if text is not None:
            elem.text = text
        return elem

    def comment(self, text: str) -> Self:
        """Appends an XML comment to group or annotate resources."""
        if self._root is None:
            raise RuntimeError("ValuesWriter must be used as a context manager.")
        sanitized = text.replace("--", "- -")
        self._root.append(ET.Comment(f" {sanitized} "))
        return self

    def string(self, **values: str) -> Self:
        """
        Appends one or more <string> resources.
        """
        for name, val in values.items():
            self._append("string", name, self._prepare_text(val))
        return self

    def boolean(self, **values: bool) -> Self:
        """
        Appends one or more <bool> resources.
        Converts Python booleans to lowercase 'true'/'false'.
        """
        for name, val in values.items():
            self._append("bool", name, str(val).lower())
        return self

    def color(self, **values: str | int) -> Self:
        """
        Appends one or more <color> resources.

        Supports hex integers (0xAARRGGBB) and
        standard Android hex strings (#RGB, #ARGB, #RRGGBB, #AARRGGBB).

        Raises:
            ValueError: If the integer range is invalid or string format is incorrect.
        """
        for name, val in values.items():
            if isinstance(val, int):
                if 0 <= val <= 0xFFFFFF:
                    color_str = f"#FF{val:06X}"
                elif 0xFFFFFF < val <= 0xFFFFFFFF:
                    color_str = f"#{val:08X}"
                else:
                    raise ValueError(
                        f"Color '{name}' has invalid integer value: {val:#x}"
                    )

            elif isinstance(val, str):
                if not _COLOR_PATTERN.match(val):
                    raise ValueError(
                        f"Color '{name}' has invalid format: '{val}'. "
                        "Expected #RGB, #ARGB, #RRGGBB, or #AARRGGBB."
                    )
                color_str = val

            else:
                raise TypeError(
                    f"Color '{name}' must be str or int, got {type(val).__name__}"
                )

            self._append("color", name, color_str.upper())
        return self

    def dimension(self, **values: Dimension) -> Self:
        """
        Appends one or more <dimen> resources using Dimension objects.
        """
        for name, val in values.items():
            self._append("dimen", name, str(val))
        return self

    def res_id(self, *values: str) -> Self:
        """
        Appends one or more <item type="id"> resources.
        Typically used in ids.xml to pre-declare resource IDs.
        """
        for name in values:
            self._append("item", name, attrs={"type": "id"})
        return self

    def integer(self, **values: int) -> Self:
        """Appends one or more <integer> resources."""
        for name, val in values.items():
            self._append("integer", name, str(val))
        return self

    def _array(
        self, tag: str, name: str, values: list[int] | list[str], escape: bool = False
    ) -> Self:
        parent = self._append(tag, name)
        for val in values:
            item = ET.SubElement(parent, "item")
            sanitized = self._prepare_text(str(val)) if escape else str(val)
            item.text = str(val).lower() if isinstance(val, bool) else sanitized
        return self

    def typed_array(self, name: str, values: list[str]) -> Self:
        """
        Appends a generic <array> (Typed Array).
        Used for arrays of references (e.g., drawables or colors).
        """
        return self._array("array", name, values)

    def integer_array(self, name: str, values: list[int]) -> Self:
        """Appends an <integer-array> resource."""
        return self._array("integer-array", name, values)

    def string_array(self, name: str, values: list[str]) -> Self:
        """Appends a <string-array> resource."""
        return self._array("string-array", name, values)

    def plurals(self, **values: PluralValues) -> Self:
        """
        Appends a <plurals> resource with quantity-specific strings.

        Args:
            name: The resource name.
            values: A dictionary of quantities (zero, one, etc.) to strings.
        """
        for name, val in values.items():
            parent = self._append("plurals", name)
            for quantity, text in val.items():
                item = ET.SubElement(parent, "item", attrib={"quantity": quantity})
                item.text = self._prepare_text(str(text))
        return self

    def style(self, name: str, parent: str | None = None, **items: str) -> Self:
        """
        Appends a <style> resource.

        Example:
            writer.style("AppTheme", parent="Theme.Material", colorPrimary="@color/blue")
        """
        attrs = {}
        if parent:
            attrs["parent"] = parent

        style_elem = self._append(
            "style", name, attrs=attrs, name_validation_pattern=_STYLE_NAME_PATTERN
        )
        for attr_name, val in items.items():
            ET.SubElement(style_elem, "item", attrib={"name": attr_name}).text = val
        return self
