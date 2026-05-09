from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

import starlark

from forje.core.context import Context, ContextProxy
from forje.core.ir import IR
from forje.dsl.module import Module
from forje.errors import ForjeEvalError, ForjeParseError

__all__ = ["run_build"]

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
    for name, value in module.python_env.items():
        if callable(value):
            mod.add_callable(name, value)
        else:
            mod[name] = value

    if starlark_env := (module.starlark_env or "").strip():
        _parse_and_eval(module.name or "build.forje", starlark_env, mod, loader)

    return mod.freeze() if into is None else mod


def _build_dsl() -> tuple[starlark.Module, Callable[..., starlark.FrozenModule]]:
    default_module = starlark.Module()

    modules: dict[str, starlark.FrozenModule] = {}

    def loader(name: str) -> starlark.FrozenModule:
        if name in modules:
            return modules[name]
        raise FileNotFoundError

    for module in Module.registry:
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
        ast = starlark.parse(name, source)
    except starlark.StarlarkError as e:
        raise ForjeParseError(str(e)) from e

    try:
        _ = starlark.eval(module, ast, _GLOBALS, starlark.FileLoader(loader))
    except starlark.StarlarkError as e:
        raise ForjeEvalError(str(e)) from e


def run_build(source: str) -> IR:
    """Evaluate a Forje build script.

    Args:
        source: The contents of a build.forje file as a string.

    Raises:
        ForjeParseError: If the source contains a Starlark syntax error.
        ForjeEvalError: If the source fails during Starlark evaluation.
    """
    ctx = Context(ir=IR())
    token = ContextProxy.set_context(ctx)

    try:
        module, loader = _build_dsl()
        _parse_and_eval("build.forje", source + "\n\nNone", module, loader)
        return ctx.ir
    finally:
        ContextProxy.reset_context(token)
