from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Self, final, override

from resforge import Color
from resforge._codegen.kotlin import KotlinFile, KotlinObject
from resforge._utils import require_context
from resforge.io import FileSystemSink, WriteSink

if TYPE_CHECKING:
    from resforge.android.types import Dimension

__all__ = ["ComposeWriter"]


@final
class _ComposeContext:
    def __init__(self, file: KotlinFile) -> None:
        self._file = file

    def add_imports(self, *fqns: str) -> None:
        for fqn in fqns:
            self._file.import_(fqn)


class _BaseComposeScope:
    def __init__(self, ctx: _ComposeContext, target: KotlinFile | KotlinObject) -> None:
        self._ctx: _ComposeContext = ctx
        self._target: KotlinFile | KotlinObject = target
        self._active: bool = False

    def __enter__(self) -> Self:
        self._active = True
        return self

    def __exit__(self, exc_type: type[BaseException] | None, *_: object) -> None:
        self._active = False

    def _to_compose_color_literal(self, color: Color) -> str:
        if color.in_srgb_gamut():
            return f"Color({color.to_srgb_argb_hex(prefix="0x")})"

        self._ctx.add_imports("androidx.compose.ui.graphics.colorspace.ColorSpaces")
        r, g, b, a = color.to_p3_components()
        return (
            f"Color(red = {r}f, green = {g}f, blue = {b}f, alpha = {a}f, "
            f"colorSpace = ColorSpaces.DisplayP3)"
        )

    @staticmethod
    def _to_compose_dimen_literal(dimen: Dimension) -> str:
        return f"{dimen.value}.{dimen.unit}"

    @require_context
    def color(self, **values: str | Color) -> Self:
        """Appends one or more Color properties to the Kotlin object."""
        if values:
            self._ctx.add_imports("androidx.compose.ui.graphics.Color")
        for name, color in values.items():
            resolved = Color.parse(color)
            self._target.property(
                name=name,
                type_="Color",
                value=self._to_compose_color_literal(resolved),
            )
        return self

    @require_context
    def dimension(self, **values: Dimension) -> Self:
        """Appends one or more Dimension properties to the Kotlin object.

        Supports dp, sp and em.

        Raises:
            ValueError: If an unsupported unit (not dp, sp, or em) is provided.
        """
        mapping = {"dp": "Dp", "sp": "Sp", "em": "TextUnit"}
        for name, dimen in values.items():
            if dimen.unit not in mapping:
                msg = "Unsupported dimension type. Only dp, sp and em are supported."
                raise ValueError(msg)
            self._ctx.add_imports(
                f"androidx.compose.ui.unit.{dimen.unit}",
                f"androidx.compose.ui.unit.{mapping[dimen.unit]}",
            )
            self._target.property(
                name=name,
                type_=mapping[dimen.unit],
                value=self._to_compose_dimen_literal(dimen),
            )

        return self


class _ObjectScope(_BaseComposeScope):
    pass


@final
class ComposeWriter(_BaseComposeScope):
    """A fluent context manager for generating Jetpack Compose color definitions.

    Writes a Kotlin file containing typed Color or Dimension properties.

    Example:
        >>> with ComposeWriter(
                "ui/theme/Color.kt",
                package="com.example.theme",
                object_name="AppColors"
            ) as compose:
        ...     compose.color(primary="#6200EE", background="#FFFFFF")
    """

    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        path: str | Path,
        package: str,
        sink: WriteSink | None = None,
    ) -> None:
        """Initializes the ComposeWriter.

        Args:
            path: The filesystem path where the Kotlin file will be saved.
            package: The Kotlin package declaration.
            sink: The custom output to write data to. If None,
                defaults to a standard file write.
        """
        self._active = False
        self._path = Path(path)
        self._package = package
        self._sink = sink or FileSystemSink()
        self._kotlin_file = KotlinFile(package=self._package)

    @override
    def __enter__(self) -> Self:  # pyright: ignore[reportMissingSuperCall]
        self._kotlin_file = KotlinFile(package=self._package)

        ctx = _ComposeContext(self._kotlin_file)
        super().__init__(ctx, self._kotlin_file)

        self._active = True

        return self

    @override
    def __exit__(  # pyright: ignore[reportMissingSuperCall]
        self,
        exc_type: type[BaseException] | None,
        *_: object,
    ) -> None:
        try:
            if exc_type is None:
                buf = BytesIO()
                self._kotlin_file.write(buf)
                self._sink.write(self._path, buf.getvalue())
        finally:
            self._active = False

    @require_context
    def object_(self, name: str) -> _ObjectScope:
        """Creates a new Kotlin object within the file.

        Args:
            name: The name of the Kotlin object to generate.

        Returns:
            A new context tied to the generated object.
        """
        obj = KotlinObject(name=name)
        self._kotlin_file.member(obj)
        return _ObjectScope(self._ctx, obj)
