import re

from pydantic import TypeAdapter

from forje.core.context import Context
from forje.core.errors import ForjeValidationError
from forje.dsl import Module
from forje.ir import ArtifactNode, TargetNode, TokenNode

__all__ = ["stdlib"]


stdlib = Module(name=None).export_starlark(
    package=__name__,
    resource_name="stdlib.star",
)

_hex_color_re = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})")
_token_adapter = TypeAdapter(TokenNode)
_artifact_adapter = TypeAdapter(ArtifactNode)


@stdlib.export(name="_sys_create_target")
def create_target(ctx: Context, id_: str) -> None:
    with ctx.lock:
        if id_ in ctx.ir.targets:
            msg = f"Duplicate target: {id_}"
            raise ForjeValidationError(msg)

        ctx.ir.targets[id_] = TargetNode(id=id_)


@stdlib.export(name="_sys_target_add_token")
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


@stdlib.export(name="_sys_target_add_artifact")
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


@stdlib.export(name="_sys_color_parse_hex")
def color_parse_hex(value: str) -> tuple[float, float, float, float]:
    if not _hex_color_re.fullmatch(value):
        msg = f"Invalid hex color: {value!r}"
        raise ValueError(msg)

    hex_str = value[1:]

    if len(hex_str) in (3, 4):
        hex_str = "".join(c * 2 for c in hex_str)

    if len(hex_str) == 6:
        hex_str = hex_str + "FF"

    r, g, b, a = bytes.fromhex(hex_str)

    return r / 255, g / 255, b / 255, a / 255
