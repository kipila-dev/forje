from __future__ import annotations

import importlib.resources
import inspect
from functools import partial
from typing import TYPE_CHECKING, Any, Self, final, overload

from forje.core.context import context_proxy

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ["Module"]


@final
class Module:
    """Manages exporting of Python definitions and Starlark sources to the DSL."""

    def __init__(self, name: str | None) -> None:
        """Initialize a new DSL module.

        Args:
            name: Starlark module name. If omitted, the exported definitions
                will be injected into the default Starlark module.
        """
        self.name = name
        self.python: dict[str, Callable[..., object] | object] = {}
        self.starlark: list[str] = []

    @overload
    def export[F: Callable[..., Any]](
        self,
        fun: F,
        *,
        name: str | None = None,
    ) -> F: ...

    @overload
    def export[F: Callable[..., Any]](
        self,
        fun: None = None,
        *,
        name: str | None = None,
    ) -> Callable[[F], F]: ...

    def export[F: Callable[..., Any]](
        self,
        fun: F | None = None,
        *,
        name: str | None = None,
    ) -> F | Callable[[F], F]:
        """Decorates a function to be exported to the DSL.

        If the function signature contains a 'ctx' parameter, it is automatically
        partially applied.

        Supports:
            @module.export
            @module.export(name="custom_name")
        """
        if fun is None:
            return partial(self.export, name=name)

        name = (name or "").strip() or fun.__name__
        sig = inspect.signature(fun)
        if "ctx" in sig.parameters:
            self.python[name] = partial(fun, context_proxy)
        else:
            self.python[name] = fun
        return fun

    def export_value(self, name: str, value: object) -> Self:
        """Exports a static value to the DSL."""
        self.python[name] = value
        return self

    def export_starlark(self, package: str, resource_name: str) -> Self:
        """Exports Starlark definitions to the DSL."""
        self.starlark.append(
            importlib.resources.files(package)
            .joinpath(resource_name)
            .read_text("utf-8"),
        )
        return self
