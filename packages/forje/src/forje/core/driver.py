from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, final, runtime_checkable

from forje.core.frontend import evaluate

if TYPE_CHECKING:
    from forje.core.environment import Environment
    from forje.ir import IR

__all__ = ["Driver", "Pass"]


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
        """Evaluates the build script and runs the pass pipeline.

        Args:
            source: Contents of a build.forje file.
            pipeline: Ordered list of passes to execute. Defaults to empty.

        Returns:
            Nested dict keyed by target id -> platform -> file path -> bytes.
        """
        ir = evaluate(self._env, source)

        for pass_ in pipeline or []:
            pass_.run(ir)

        return ir.outputs
