import importlib.metadata

from forje.backend import Backend
from forje.core.errors import ForjePluginLoadError
from forje.dsl import Module

__all__ = ["load_plugins"]


def load_plugins() -> tuple[list[Module], dict[str, Backend]]:
    """Discovers and loads all registered Forje DSL modules and backends.

    Returns:
        A tuple containing a list of loaded `Module` instances and a
        dictionary mapping `Backend` names to their instances.

    Raises:
        ForjePluginLoadError: If a plugin fails to resolve, fails to
            instantiate, or does not match the expected type.
    """
    dsl_modules: list[Module] = []
    for ep in importlib.metadata.entry_points(group="forje.dsl"):
        try:
            module = ep.load()  # pyright: ignore[reportAny]
        except Exception as e:
            msg = f"Failed to resolve entry point for plugin '{ep.name}': {e}"
            raise ForjePluginLoadError(msg) from e

        if not isinstance(module, Module):
            msg = f"Invalid plugin '{ep.name}': must resolve to a Module instance"
            raise ForjePluginLoadError(msg)

        dsl_modules.append(module)

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

    return dsl_modules, backends
