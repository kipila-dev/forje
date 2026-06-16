__all__ = ["Pass"]


from typing import Protocol, runtime_checkable

from forje.ir import IR


@runtime_checkable
class Pass(Protocol):
    """A compiler pass.

    Passes are executed sequentially by the `Driver` pipeline and are allowed
    to modify the `IR` in-place.
    """

    def run(self, ir: IR) -> None:
        """Executes the compiler pass logic on the given IR instance."""
