import importlib.metadata

from forje.backend import Backend
from forje.core.errors import ForjePluginLoadError
from forje.core.pass_ import Pass
from forje.dsl import Module

__all__ = ["load_plugins"]


def load_plugins() -> tuple[list[Module], list[Pass], dict[str, Backend]]:
    """Discovers and loads all registered Forje DSL modules and backends.

    Returns:
        A 3-tuple of: loaded DSL modules, instantiated compiler passes,
        and a dict mapping platform names to backend instances.

    Raises:
        ForjePluginLoadError: If a plugin fails to resolve, fails to
            instantiate, or does not match the expected type.
    """
    modules: list[Module] = []
    for ep in importlib.metadata.entry_points(group="forje.dsl"):
        try:
            module = ep.load()  # pyright: ignore[reportAny]
        except Exception as e:
            msg = f"Failed to resolve entry point for plugin '{ep.name}': {e}"
            raise ForjePluginLoadError(msg) from e

        if not isinstance(module, Module):
            msg = f"Invalid plugin '{ep.name}': must resolve to a Module instance"
            raise ForjePluginLoadError(msg)

        modules.append(module)

    passes: list[Pass] = []
    for ep in importlib.metadata.entry_points(group="forje.pass"):
        try:
            pass_ = ep.load()()  # pyright: ignore[reportAny]
        except Exception as e:
            msg = f"Failed to resolve entry point for compiler pass '{ep.name}': {e}"
            raise ForjePluginLoadError(msg) from e

        if not isinstance(pass_, Pass):
            msg = f"Invalid plugin '{ep.name}': must resolve to a Pass instance"
            raise ForjePluginLoadError(msg)

        passes.append(pass_)

    backends: dict[str, Backend] = {}
    for ep in importlib.metadata.entry_points(group="forje.backend"):
        try:
            backend = ep.load()()  # pyright: ignore[reportAny]
        except Exception as e:
            msg = f"Failed to load backend '{ep.name}': {e}"
            raise ForjePluginLoadError(msg) from e

        if not isinstance(backend, Backend):
            msg = f"Invalid plugin '{ep.name}': must resolve to a Backend instance"
            raise ForjePluginLoadError(msg)

        backends[ep.name] = backend

    return modules, passes, backends
