from forje.core.ir import IR, TargetIR
from forje.dsl import ForjeModule

stdlib = ForjeModule(name=None)


@stdlib.export
def target(ctx: IR, name: str) -> None:
    ctx.targets.append(TargetIR(name))
