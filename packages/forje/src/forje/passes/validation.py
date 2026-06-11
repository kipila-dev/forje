from typing import final, override

from forje.core.driver import Pass
from forje.core.environment import Environment
from forje.core.errors import ForjeError
from forje.ir import IR

__all__ = ["PlatformSupport", "TargetFilter"]


@final
class TargetFilter(Pass):
    """Restricts the active targets to the specified subset.

    If no targets are provided, all targets are kept.
    """

    def __init__(self, active_targets: list[str] | None = None) -> None:
        self._active_targets = active_targets or []

    @override
    def run(self, ir: IR) -> None:
        if self._active_targets:
            all_targets = [t.id for t in ir.targets.values()]
            unknown_targets = [t for t in self._active_targets if t not in all_targets]
            if unknown_targets:
                noun = "target" if len(unknown_targets) == 1 else "targets"
                msg = f"Unknown {noun}: {', '.join(unknown_targets)}"
                raise ForjeError(msg)

            ir.targets = {
                k: v for k, v in ir.targets.items() if k in self._active_targets
            }

        if not ir.targets:
            msg = "No targets defined in the build configuration"
            raise ForjeError(msg)


@final
class PlatformSupport(Pass):
    """Verifies that every artifact platform has a registered backend."""

    def __init__(self, env: Environment) -> None:
        self._env = env

    @override
    def run(self, ir: IR) -> None:
        all_platforms = self._env.backends.keys()
        active_platforms = {
            a.platform for t in ir.targets.values() for a in t.artifacts
        }
        unknown_platforms = active_platforms - all_platforms
        if unknown_platforms:
            platforms = ", ".join(f"'{p}'" for p in sorted(unknown_platforms))
            msg = f"No backend registered for platforms: {platforms}"
            raise ForjeError(msg)
