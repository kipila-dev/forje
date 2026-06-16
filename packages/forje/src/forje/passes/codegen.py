from typing import final, override

from forje.core.environment import Environment
from forje.core.pass_ import Pass
from forje.ir import IR


@final
class Codegen(Pass):
    """Executes code generation for all targets."""

    def __init__(self, env: Environment) -> None:
        self._env = env

    @override
    def run(self, ir: IR) -> None:
        for target in ir.targets.values():
            ir.outputs[target.id] = {}
            for artifact in target.artifacts:
                files = self._env.backends[artifact.platform].codegen(target, artifact)
                ir.outputs[target.id][artifact.platform] = files
