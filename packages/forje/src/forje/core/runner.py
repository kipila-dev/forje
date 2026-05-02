import starlark

from forje.errors import ForjeEvalError, ForjeParseError


def run_build(source: str) -> None:
    module = starlark.Module()
    globals_ = starlark.Globals.extended_by([starlark.LibraryExtension.Print])

    try:
        ast = starlark.parse("build.forje", source)
    except starlark.StarlarkError as e:
        raise ForjeParseError(str(e)) from e

    try:
        _ = starlark.eval(module, ast, globals_)
    except starlark.StarlarkError as e:
        raise ForjeEvalError(str(e)) from e
