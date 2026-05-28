from typing import final

from forje.backend import Backend
from forje.dsl import Module

__all__ = ["Environment"]


@final
class Environment:
    """Represents the global configuration and available plugins for a Forje build.

    It is intended to be initialized once by the build system and passed into
    the `Driver` and `Pass` objects.

    Attributes:
        dsl_modules: A list of registered DSL modules available for compilation.
        backends: A dictionary mapping platform names to their configured
            backend instances.
    """

    def __init__(self, dsl_modules: list[Module], backends: dict[str, Backend]) -> None:
        self.dsl_modules = dsl_modules
        self.backends = backends
