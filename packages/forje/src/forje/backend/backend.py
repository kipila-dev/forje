from typing import Protocol

from forje.ir import IR

__all__ = ["Backend"]


class Backend(Protocol):
    def codegen(self, ir: IR) -> None: ...
