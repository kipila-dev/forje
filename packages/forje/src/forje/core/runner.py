from collections.abc import Callable

import starlark

from forje.core import IR
from forje.dsl import ForjeModule, load_core, load_extensions
from forje.errors import ForjeEvalError, ForjeParseError

__all__ = ["run_build"]

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
    for module in ForjeModule.register:
        if module.name is None:
            _build_module(module, into=default_module)
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
    ctx = IR()
    token = ForjeModule.set_context(ctx)

    try:
        module = starlark.Module()
        loader = _build_dsl(default_module=module)

        globals_ = starlark.Globals.standard().extended_by(
            [starlark.LibraryExtension.Print, starlark.LibraryExtension.StructType],
        )

        try:
            ast = starlark.parse("build.forje", source)
        except starlark.StarlarkError as e:
            raise ForjeParseError(str(e)) from e

        try:
            _ = starlark.eval(module, ast, globals_, starlark.FileLoader(loader))
        except starlark.StarlarkError as e:
            raise ForjeEvalError(str(e)) from e

        return ctx
    finally:
        ForjeModule.reset_context(token)
