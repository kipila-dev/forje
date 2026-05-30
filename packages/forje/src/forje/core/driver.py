from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, final, runtime_checkable

from forje.core.compiler import compile_
from forje.core.errors import ForjeError

if TYPE_CHECKING:
    from forje.core.environment import Environment
    from forje.ir import IR

__all__ = ["Driver", "Pass"]


def _wrap_error(e: BaseException, pass_name: str) -> ForjeError:
    msg = f"{e} [{pass_name}]"
    return ForjeError(msg)


@runtime_checkable
class Pass(Protocol):
    """A compiler pass.

    Passes are executed sequentially by the `Driver` pipeline and modify the `IR`
    in-place.
    """

    def run(self, ir: IR) -> None:
        """Executes the compiler pass logic on the given IR instance."""
        ...


@final
class Driver:
    """Orchestrates the compilation and artifact generation pipeline."""

    def __init__(self, env: Environment) -> None:
        self._env = env

    def build(
        self,
        source: str,
        pipeline: list[Pass] | None = None,
    ) -> dict[str, dict[str, dict[str, bytes]]]:
        """Compiles Starlark source and runs the pipeline."""
        ir = compile_(self._env, source)

        for pass_ in pipeline or []:
            try:
                pass_.run(ir)
            except* Exception as eg:
                for e in eg.exceptions:
                    e.add_note(f"[{pass_.__class__.__name__}]")
                raise

        return ir.outputs
