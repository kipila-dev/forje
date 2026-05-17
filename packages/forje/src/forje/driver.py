import importlib.metadata
from typing import TYPE_CHECKING, final

from rich import print  # noqa: A004

from forje.core.compiler import compile_
from forje.core.environment import Environment
from forje.errors import ForjeError

if TYPE_CHECKING:
    from forje.backend import Backend

__all__ = ["Driver"]


@final
class Driver:
    def __init__(self, env: Environment) -> None:
        self._env = env
        self._backends: dict[str, Backend] = {
            ep.name: ep.load()()
            for ep in importlib.metadata.entry_points(group="forje.backend")
        }

    def build(self, source: str) -> None:
        ir = compile_(self._env, source)
        print(ir)

        active = {
            artifact.platform
            for target in ir.targets.values()
            for artifact in target.artifacts
        }
        unknown = active - self._backends.keys()

        if unknown:
            platforms = ", ".join(f"'{p}'" for p in sorted(unknown))
            msg = f"No backend registered for platforms: {platforms}"
            raise ForjeError(msg) from None

        for platform in active:
            self._backends[platform].codegen(ir)
