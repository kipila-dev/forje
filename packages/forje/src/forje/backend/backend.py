from typing import Protocol, runtime_checkable

from forje.ir import ArtifactNode, TargetNode

__all__ = ["Backend"]


@runtime_checkable
class Backend(Protocol):
    def codegen(
        self,
        target: TargetNode,
        artifact: ArtifactNode,
    ) -> dict[str, bytes]: ...
