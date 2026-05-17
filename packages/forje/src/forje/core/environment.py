import importlib.metadata
from typing import Self

from forje.dsl import Module
from forje.dsl.stdlib import stdlib
from forje.errors import ForjePluginLoadError


class Environment:
    def __init__(self) -> None:
        self.modules: list[Module] = [stdlib]

    def load_plugins(self) -> Self:
        for ep in importlib.metadata.entry_points(group="forje.dsl.plugin"):
            try:
                module = ep.load()  # pyright: ignore[reportAny]

                if not isinstance(module, Module):
                    msg = (
                        f"Invalid plugin '{ep.name}': must resolve to a Module instance"
                    )
                    raise ForjePluginLoadError(msg)

                self.modules.append(module)
            except (ImportError, AttributeError) as e:
                msg = f"Failed to resolve entry point for plugin '{ep.name}': {e}"
                raise ForjePluginLoadError(msg) from e

        return self
