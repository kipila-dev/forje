import re
import xml.etree.ElementTree as ET
from pathlib import Path
from re import Pattern
from typing import Self

from resforge._utils import atomic_write, require_context
from resforge.types import Color

from .types import Dimension, PluralValues

__all__ = ["ValuesWriter"]

_NAME_PATTERN = re.compile(r"^[a-z_][a-z0-9_]*$")
_STYLE_NAME_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_\.]*$")


class ValuesWriter:
    """A fluent context manager for generating Android XML resource files.

    Provides a type-safe interface for creating strings, dimensions, colors,
    and arrays. Validates resource names and color formats at runtime.

    Example:
        >>> with ValuesWriter("res/values/resources.xml") as res:
        ...     res.dimension(padding_small=dp(8)).color(primary="#FF0000")

    """

    def __init__(self, path: str | Path) -> None:
        """Initializes the ValuesWriter.

        Args:
            path: The filesystem path where the XML will be saved.

        """
        self._path = Path(path)
        self._active = False

        # Structure: {"string": ["app_name"], ...}
        self._names: dict[str, set[str]] = {}

    def __enter__(self) -> Self:
        self._active = True
        self._root = ET.Element("resources")
        self._names.clear()
        return self

    def __exit__(self, exc_type, *_) -> None:
        try:
            if exc_type is None:
                ET.indent(self._root, space=" " * 4, level=0)
                tree = ET.ElementTree(self._root)
                with atomic_write(self._path) as tf:
                    tree.write(
                        tf,
                        encoding="utf-8",
                        xml_declaration=True,
                        short_empty_elements=True,
                    )
        finally:
            self._active = False

    def _sanitize(self, text: str) -> str:
        text = text.replace("'", r"\'")
        text = text.replace('"', r"\"")
        text = text.replace("\n", r"\n")
        if text.startswith(("@", "?")):
            text = "\\" + text
        return text

    def _validate_name(
        self, tag: str, name: str, pattern: Pattern[str] = _NAME_PATTERN
    ) -> None:
        if not pattern.match(name):
            msg = f"Invalid resource name '{name}'."
            raise ValueError(msg)

        names_for_tag = self._names.setdefault(tag, set())
        if name in names_for_tag:
            msg = f"Duplicate resource name '{name}' for tag <{tag}>."
            raise ValueError(msg)
        names_for_tag.add(name)

    def _append(
        self,
        tag: str,
        name: str,
        text: str | None = None,
        attrs: dict[str, str] | None = None,
        pattern: Pattern[str] = _NAME_PATTERN,
    ) -> ET.Element:
        self._validate_name(tag, name, pattern)
        attrs = {"name": name, **(attrs or {})}
        elem = ET.SubElement(self._root, tag, attrib=attrs)
        if text is not None:
            elem.text = text
        return elem

    def _append_array(
        self,
        tag: str,
        name: str,
        values: list[int] | list[str],
        *,
        sanitize: bool = False,
    ) -> Self:
        parent = self._append(tag, name)
        for val in values:
            item = ET.SubElement(parent, "item")
            sanitized = self._sanitize(str(val)) if sanitize else str(val)
            item.text = str(val).lower() if isinstance(val, bool) else sanitized
        return self

    @require_context
    def comment(self, text: str) -> Self:
        """Appends an XML comment."""
        sanitized = text.replace("--", "- -")
        self._root.append(ET.Comment(f" {sanitized} "))
        return self

    @require_context
    def string(self, **values: str) -> Self:
        """Appends one or more <string> resources."""
        for name, val in values.items():
            self._append("string", name, self._sanitize(val))
        return self

    @require_context
    def boolean(self, **values: bool) -> Self:
        """Appends one or more <bool> resources."""
        for name, val in values.items():
            self._append("bool", name, str(val).lower())
        return self

    @require_context
    def color(self, **values: str | Color) -> Self:
        """Appends one or more <color> resources.

        Supported hex string formats are #RGB, #ARGB, #RRGGBB, #AARRGGBB.

        Raises:
            ValueError: If the string format is incorrect.

        """
        for name, color in values.items():
            resolved = Color(color)
            self._append("color", name, resolved.hex)
        return self

    @require_context
    def dimension(self, **values: Dimension) -> Self:
        """Appends one or more <dimen> resources."""
        for name, val in values.items():
            self._append("dimen", name, str(val))
        return self

    @require_context
    def res_id(self, *values: str) -> Self:
        """Appends one or more <item type="id"> resources."""
        for name in values:
            self._append("item", name, attrs={"type": "id"})
        return self

    @require_context
    def integer(self, **values: int) -> Self:
        """Appends one or more <integer> resources."""
        for name, val in values.items():
            self._append("integer", name, str(val))
        return self

    @require_context
    def plurals(self, **values: PluralValues) -> Self:
        """Appends one or more <plurals> resources."""
        for name, val in values.items():
            parent = self._append("plurals", name)
            for quantity, text in val.items():
                item = ET.SubElement(parent, "item", attrib={"quantity": quantity})
                item.text = self._sanitize(str(text))
        return self

    @require_context
    def typed_array(self, name: str, values: list[str]) -> Self:
        """Appends a generic <array> resource."""
        return self._append_array("array", name, values)

    @require_context
    def integer_array(self, name: str, values: list[int]) -> Self:
        """Appends an <integer-array> resource."""
        return self._append_array("integer-array", name, values)

    @require_context
    def string_array(self, name: str, values: list[str]) -> Self:
        """Appends a <string-array> resource."""
        return self._append_array("string-array", name, values, sanitize=True)

    @require_context
    def style(self, name: str, parent: str | None = None, **items: str) -> Self:
        """Appends a <style> resource."""
        attrs = {}
        if parent:
            attrs["parent"] = parent

        style_elem = self._append(
            "style", name, attrs=attrs, pattern=_STYLE_NAME_PATTERN
        )
        for attr_name, val in items.items():
            ET.SubElement(style_elem, "item", attrib={"name": attr_name}).text = val
        return self
