from collections.abc import Callable

import starlark

from forje.core import IR
from forje.dsl import ForjeModule, load_core, load_extensions
from forje.errors import ForjeEvalError, ForjeParseError

__all__ = ["run_build"]

_STARLARK_EXTENSIONS = [
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
]

load_core()
load_extensions()


def _build_module(
    module: ForjeModule,
    into: starlark.Module | None = None,
) -> starlark.Module | starlark.FrozenModule:
    mod = starlark.Module() if into is None else into
    for name, value in module.env.items():
        if callable(value):
            mod.add_callable(name, value)
        else:
            mod[name] = value
    return mod.freeze() if into is None else mod


def _build_dsl(
    default_module: starlark.Module,
) -> Callable[..., starlark.FrozenModule]:
    modules: dict[str, starlark.FrozenModule] = {}
    for module in ForjeModule.registry:
        if module.name is None:
            _ = _build_module(module, into=default_module)
        else:
            mod = _build_module(module)
            if isinstance(mod, starlark.FrozenModule):
                modules[module.name] = mod

    def loader(name: str) -> starlark.FrozenModule:
        if name in modules:
            return modules[name]
        raise FileNotFoundError

    return loader


def run_build(source: str) -> IR:
    """Evaluate a Forje build script.

    Args:
        source: The contents of a build.forje file as a string.

    Raises:
        ForjeParseError: If the source contains a Starlark syntax error.
        ForjeEvalError: If the source fails during Starlark evaluation.
    """
    ctx = IR()
    token = ForjeModule.set_context(ctx)

    try:
        module = starlark.Module()
        loader = _build_dsl(default_module=module)

        globals_ = starlark.Globals.standard().extended_by(_STARLARK_EXTENSIONS)

        try:
            ast = starlark.parse("build.forje", source)
        except starlark.StarlarkError as e:
            raise ForjeParseError(str(e)) from e

        try:
            _ = starlark.eval(module, ast, globals_, starlark.FileLoader(loader))
        except starlark.StarlarkError as e:
            raise ForjeEvalError(str(e)) from e
    finally:
        ForjeModule.reset_context(token)

    return ctx
