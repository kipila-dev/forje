from __future__ import annotations

import importlib.metadata
import importlib.resources
import inspect
from functools import partial
from pkgutil import iter_modules
from typing import TYPE_CHECKING, Any, ClassVar, Self, final, overload

import forje.dsl.core
from forje.core.context import ContextProxy

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ["Module", "load_dsl_core", "load_dsl_extensions"]


@final
class Module:
    """Manages exporting of Python functions to the DSL."""

    _ctx = ContextProxy()
    registry: ClassVar[list[Module]] = []

    def __init__(self, name: str | None) -> None:
        """Initialize a new DSL module.

        Args:
            name: Starlark module name. If omitted, the exports will be injected
                into the default Starlark module.
        """
        self.name = name
        self.python_env: dict[str, Callable[..., object] | object] = {}
        self.starlark_env: str | None = None
        Module.registry.append(self)

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

        resolved_name = (name if name and name.strip() else fun.__name__).strip()
        sig = inspect.signature(fun)
        if "ctx" in sig.parameters:
            self.python_env[resolved_name] = partial(fun, Module._ctx)
        else:
            self.python_env[resolved_name] = fun
        return fun

    def export_value(self, name: str, value: object) -> Self:
        """Exports a static value to the DSL."""
        self.python_env[name] = value
        return self

    def export_starlark(self, package: str, resource_name: str) -> Self:
        """Exports Starlark definitions to the DSL."""
        self.starlark_env = (
            importlib.resources.files(package)
            .joinpath(resource_name)
            .read_text("utf-8")
        )
        return self


def load_dsl_core() -> None:
    """Imports all submodules from the core DSL package.

    This triggers the execution of @module.export decorators within the core library.
    """
    for _, name, _ in iter_modules(forje.dsl.core.__path__):
        full_name = f"forje.dsl.core.{name}"
        _ = importlib.import_module(full_name)


def load_dsl_extensions() -> None:
    """Loads external DSL extensions."""
    entries = importlib.metadata.entry_points(group="forje.dsl.extensions")
    for entry in entries:
        entry.load()
