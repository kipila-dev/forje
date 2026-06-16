from dataclasses import dataclass
from typing import final

from forje.backend import Backend
from forje.core.pass_ import Pass
from forje.dsl import Module

__all__ = ["Environment"]


@final
@dataclass(frozen=True)
class Environment:
    """Global configuration and available plugins for a Forje build.

    It is intended to be initialized once by the build system and passed into
    the `Driver` and `Pass` objects.
    """

    modules: list[Module]
    passes: list[Pass]
    backends: dict[str, Backend]
