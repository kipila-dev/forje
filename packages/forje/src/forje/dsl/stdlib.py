from pydantic import TypeAdapter

from forje.core.context import Context
from forje.core.errors import ForjeValidationError
from forje.dsl import Module
from forje.ir import ArtifactNode, TargetNode, TokenNode

__all__ = ["module"]

module = Module(name=None).export_starlark(
    package=__name__,
    resource_name="stdlib.star",
)

_token_adapter = TypeAdapter(TokenNode)
_artifact_adapter = TypeAdapter(ArtifactNode)


@module.export(name="_sys_create_target")
def create_target(ctx: Context, id_: str) -> None:
    with ctx.lock:
        if id_ in ctx.ir.targets:
            msg = f"Duplicate target: {id_}"
            raise ForjeValidationError(msg)

        ctx.ir.targets[id_] = TargetNode(id=id_)


@module.export(name="_sys_target_add_token")
def target_add_token(
    ctx: Context,
    target_id: str,
    token: dict[str, object],
) -> None:
    parsed = _token_adapter.validate_python(token)
    with ctx.lock:
        try:
            target = ctx.ir.targets[target_id]
        except LookupError:
            msg = f"Invalid target: {target_id}"
            raise ForjeValidationError(msg) from None
        target.tokens[parsed.name] = parsed


@module.export(name="_sys_target_add_artifact")
def target_add_artifact(
    ctx: Context,
    target_id: str,
    artifact: dict[str, object],
) -> None:
    parsed = _artifact_adapter.validate_python(artifact)
    with ctx.lock:
        try:
            target = ctx.ir.targets[target_id]
        except LookupError:
            msg = f"Invalid target: {target_id}"
            raise ForjeValidationError(msg) from None
        target.artifacts.append(parsed)
