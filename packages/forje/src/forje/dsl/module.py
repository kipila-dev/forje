from __future__ import annotations

import importlib.metadata
import inspect
from contextvars import ContextVar, Token
from functools import partial
from pkgutil import iter_modules
from typing import TYPE_CHECKING, Any, ClassVar, final, override

import forje.dsl.core

if TYPE_CHECKING:
    from collections.abc import Callable

    from forje.core.ir import IR


__all__ = ["ForjeModule", "load_core", "load_extensions"]

_ir_var: ContextVar[IR] = ContextVar("ir_var")


class _IRProxy:
    def __getattr__(self, name: str) -> object:
        try:
            return getattr(_ir_var.get(), name)  # pyright: ignore[reportAny]
        except LookupError:
            msg = "No IR context active."
            raise RuntimeError(msg) from LookupError

    @override
    def __repr__(self) -> str:
        try:
            return repr(_ir_var.get())
        except LookupError:
            return "<Empty IR Proxy>"


@final
class ForjeModule:
    """Manages exporting of Python functions to the DSL."""

    _ir = _IRProxy()
    registry: ClassVar[list[ForjeModule]] = []

    def __init__(self, name: str | None) -> None:
        """Initialize a new module.

        Args:
            name: Starlark module name. If omitted, the exports will be injected
                into the default Starlark module.
        """
        self.name = name
        self.env: dict[str, Callable[..., object] | object] = {}
        ForjeModule.registry.append(self)

    def export[F: Callable[..., Any]](self, fun: F) -> F:
        """Decorates a function to be exported to the DSL.

        If the function signature contains a 'ctx' parameter, it is automatically
        partially applied with the IR context proxy.
        """
        sig = inspect.signature(fun)
        if "ctx" in sig.parameters:
            self.env[fun.__name__] = partial(fun, ForjeModule._ir)
        else:
            self.env[fun.__name__] = fun
        return fun

    def export_value(self, name: str, value: object) -> None:
        """Exports a static value to the DSL."""
        self.env[name] = value

    @classmethod
    def set_context(cls, ctx: IR) -> Token[IR]:
        """Sets the IR for the current execution context."""
        return _ir_var.set(ctx)

    @classmethod
    def reset_context(cls, token: Token[IR]) -> None:
        """Resets the context to the state before set_context was called."""
        _ir_var.reset(token)


def load_core() -> None:
    """Imports all submodules from the core DSL package.

    This triggers the execution of @module.export decorators within the core library.
    """
    for _, name, _ in iter_modules(forje.dsl.core.__path__):
        full_name = f"forje.dsl.core.{name}"
        _ = importlib.import_module(full_name)


def load_extensions() -> None:
    """Loads external DSL extensions."""
    entries = importlib.metadata.entry_points(group="forje.dsl.extensions")
    for entry in entries:
        entry.load()
