from forje.core.ir import IR
from forje.dsl import ForjeModule

stdlib = ForjeModule(name=None)


@stdlib.export
def target(ctx: IR, name: str) -> None:
    print(f"Hello from target({name})! Context is {ctx}")
