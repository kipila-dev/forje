from __future__ import annotations

import importlib.metadata
from typing import TYPE_CHECKING, final

from forje.core.compiler import compile_
from forje.errors import ForjeError

if TYPE_CHECKING:
    from forje.backend import Backend
    from forje.core.environment import Environment
    from forje.ir import IR, ArtifactNode, TargetNode

__all__ = ["Driver"]


@final
class Driver:
    """Orchestrates the compilation and artifact generation pipeline."""

    def __init__(self, env: Environment) -> None:
        self._env = env
        self._backends: dict[str, Backend] = {
            ep.name: ep.load()()
            for ep in importlib.metadata.entry_points(group="forje.backend")
        }

    def build(
        self,
        source: str,
        targets: list[str] | None = None,
    ) -> dict[str, dict[str, dict[str, bytes]]]:
        """Compiles Starlark source and runs codegen for the specified targets."""
        ir = compile_(self._env, source)

        self._validate_requested_targets(ir, targets)

        active_targets = (
            [t for t in ir.targets.values() if t.id in targets]
            if targets
            else ir.targets.values()
        )

        tasks = [(t, a) for t in active_targets for a in t.artifacts]

        self._validate_platform_support(tasks)

        return self._execute_codegen(tasks)

    def _validate_requested_targets(self, ir: IR, targets: list[str] | None) -> None:
        if targets:
            unknown_targets = sorted(set(targets) - {t.id for t in ir.targets.values()})
            if unknown_targets:
                msg = f"Unknown target: {", ".join(unknown_targets)}"
                raise ForjeError(msg)

    def _validate_platform_support(
        self,
        tasks: list[tuple[TargetNode, ArtifactNode]],
    ) -> None:
        active_platforms = {artifact.platform for _, artifact in tasks}
        unknown_platforms = active_platforms - self._backends.keys()
        if unknown_platforms:
            platforms = ", ".join(f"'{p}'" for p in sorted(unknown_platforms))
            msg = f"No backend registered for platforms: {platforms}"
            raise ForjeError(msg) from None

    def _execute_codegen(
        self,
        tasks: list[tuple[TargetNode, ArtifactNode]],
    ) -> dict[str, dict[str, dict[str, bytes]]]:
        results: dict[str, dict[str, dict[str, bytes]]] = {}
        for target, artifact in tasks:
            try:
                target_map = results.setdefault(target.id, {})
                target_map[artifact.platform] = self._backends[
                    artifact.platform
                ].codegen(target, artifact)
            except Exception as e:
                msg = (
                    f"Codegen failed for target '{target.id}' "
                    f"on '{artifact.platform}': {e}"
                )
                raise ForjeError(msg) from e
        return results
