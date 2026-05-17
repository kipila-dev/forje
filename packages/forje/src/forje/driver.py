from typing import final

from rich import print  # noqa: A004

from forje.core.compiler import compile_
from forje.core.environment import Environment

__all__ = ["Driver"]


@final
class Driver:
    def __init__(self, env: Environment) -> None:
        self._env = env

    def build(self, source: str) -> None:
        ir = compile_(self._env, source)
        print(ir)
