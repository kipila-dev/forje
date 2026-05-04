from __future__ import annotations

import importlib.metadata
import inspect
from functools import partial
from pkgutil import iter_modules
from typing import TYPE_CHECKING, Any, ClassVar

import forje.dsl.core

if TYPE_CHECKING:
    from collections.abc import Callable

    from forje.core.ir import IR


__all__ = ["ForjeModule", "load_core", "load_extensions"]


class _IRProxy:
    def __init__(self) -> None:
        self.__dict__["_real_ir"] = None

    def set_target(self, ir: IR) -> None:
        self.__dict__["_real_ir"] = ir

    def __getattr__(self, name: str) -> Any:
        if self._real_ir is None:
            msg = "Attempted to access IR attribute before it was built."
            raise RuntimeError(msg)
        return getattr(self._real_ir, name)

    def __repr__(self) -> str:
        return repr(self._real_ir) if self._real_ir else "<Empty IR Proxy>"


class ForjeModule:
    _ir = _IRProxy()
    register: ClassVar[list[ForjeModule]] = []

    def __init__(self, name: str | None) -> None:
        self.name = name
        self.env: dict[str, Callable[..., Any] | Any] = {}
        ForjeModule.register.append(self)

    def export[F: Callable[..., Any]](self, fun: F) -> F:
        sig = inspect.signature(fun)
        if "ctx" in sig.parameters:
            self.env[fun.__name__] = partial(fun, ForjeModule._ir)
        else:
            self.env[fun.__name__] = fun
        return fun

    def export_value(self, name: str, value: object) -> None:
        self.env[name] = value

    @classmethod
    def register_context(cls, ctx: IR) -> None:
        cls._ir.set_target(ctx)


def load_core() -> None:
    for _, name, _ in iter_modules(forje.dsl.core.__path__):
        full_name = f"forje.dsl.core.{name}"
        importlib.import_module(full_name)


def load_extensions() -> None:
    entries = importlib.metadata.entry_points(group="forje.dsl.extensions")
    for entry in entries:
        entry.load()
