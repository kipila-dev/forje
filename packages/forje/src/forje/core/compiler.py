from __future__ import annotations

from typing import TYPE_CHECKING

import starlark

from forje.core import Context
from forje.core.context import context_proxy
from forje.errors import ForjeEvalError, ForjeParseError
from forje.ir import IR

if TYPE_CHECKING:
    from collections.abc import Callable

    from forje.core.environment import Environment
    from forje.dsl.module import Module

__all__ = ["compile_"]

_DIALECT = starlark.Dialect.extended()
_GLOBALS = starlark.Globals.standard().extended_by(
    [
        starlark.LibraryExtension.EnumType,
        starlark.LibraryExtension.Filter,
        starlark.LibraryExtension.Json,
        starlark.LibraryExtension.Map,
        starlark.LibraryExtension.Partial,
        starlark.LibraryExtension.Pprint,
        starlark.LibraryExtension.Print,
        starlark.LibraryExtension.RecordType,
        starlark.LibraryExtension.RustDecimal,
        starlark.LibraryExtension.StructType,
        starlark.LibraryExtension.Typing,
    ],
)


def _build_module(
    module: Module,
    loader: Callable[..., starlark.FrozenModule],
    into: starlark.Module | None = None,
) -> starlark.Module | starlark.FrozenModule:
    mod = starlark.Module() if into is None else into
    for name, value in module.python.items():
        if callable(value):
            mod.add_callable(name, value)
        else:
            mod[name] = value

    for script in module.starlark:
        _parse_and_eval(module.name or "build.forje", script, mod, loader)

    return mod.freeze() if into is None else mod


def _build_dsl(
    env: Environment,
) -> tuple[starlark.Module, Callable[..., starlark.FrozenModule]]:

    modules: dict[str, starlark.FrozenModule] = {}
    default_module = starlark.Module()

    def loader(name: str) -> starlark.FrozenModule:
        if name in modules:
            return modules[name]
        raise FileNotFoundError

    for module in env.modules:
        if module.name is None:
            _ = _build_module(module, loader, into=default_module)
        else:
            mod = _build_module(module, loader)
            if isinstance(mod, starlark.FrozenModule):
                modules[module.name] = mod

    return default_module, loader


def _parse_and_eval(
    name: str,
    source: str,
    module: starlark.Module,
    loader: Callable[..., starlark.FrozenModule],
) -> None:
    try:
        ast = starlark.parse(name, source, dialect=_DIALECT)
    except starlark.StarlarkError as e:
        raise ForjeParseError(str(e)) from e

    try:
        _ = starlark.eval(module, ast, _GLOBALS, starlark.FileLoader(loader))
    except starlark.StarlarkError as e:
        raise ForjeEvalError(str(e)) from e


def compile_(env: Environment, source: str) -> IR:
    """Evaluate a Forje build script.

    Args:
        env: The build environment instance containing the standard library
            and all successfully discovered external modules.
        source: The contents of a build.forje file as a string.

    Raises:
        ForjeParseError: If the source contains a Starlark syntax error.
        ForjeEvalError: If the source fails during Starlark evaluation.
    """
    ctx = Context(ir=IR())
    token = context_proxy.set_context(ctx)

    try:
        module, loader = _build_dsl(env)
        _parse_and_eval("build.forje", source + "\n\nNone", module, loader)
        return ctx.ir
    finally:
        context_proxy.reset_context(token)
