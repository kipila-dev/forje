import importlib.metadata
from typing import Self

from forje.dsl import Module
from forje.errors import ForjePluginLoadError


class Environment:
    def __init__(self) -> None:
        self.modules: list[Module] = []

    def load_plugins(self) -> Self:
        for ep in importlib.metadata.entry_points(group="forje.dsl"):
            try:
                module = ep.load()  # pyright: ignore[reportAny]
            except Exception as e:
                msg = f"Failed to resolve entry point for plugin '{ep.name}': {e}"
                raise ForjePluginLoadError(msg) from e

            if not isinstance(module, Module):
                msg = f"Invalid plugin '{ep.name}': must resolve to a Module instance"
                raise ForjePluginLoadError(msg)

            self.modules.append(module)

        return self
