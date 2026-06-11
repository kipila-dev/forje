from typing import Protocol, runtime_checkable

from forje.ir import ArtifactNode, TargetNode

__all__ = ["Backend"]


@runtime_checkable
class Backend(Protocol):
    """Interface for platform-specific code generators."""

    def codegen(
        self,
        target: TargetNode,
        artifact: ArtifactNode,
    ) -> dict[str, bytes]:
        """Generates platform assets for a target.

        Returns:
            File paths relative to the base directory mapped to their contents.
        """
        ...
