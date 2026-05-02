class ForjeError(Exception):
    """Base class for all Forje errors."""


class ForjeParseError(ForjeError):
    """Starlark parse error in build.forje."""


class ForjeEvalError(ForjeError):
    """Starlark evaluation error in build.forje."""
