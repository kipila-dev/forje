from typing import Protocol

from forje.ir import ArtifactNode, TargetNode

__all__ = ["Backend"]


class Backend(Protocol):
    def codegen(
        self,
        target: TargetNode,
        artifact: ArtifactNode,
    ) -> dict[str, bytes]: ...
