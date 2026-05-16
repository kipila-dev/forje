import re

from forje.core.context import Context
from forje.core.ir import TargetIR, TokenIR, ValueIR
from forje.dsl import Module
from forje.errors import ForjeValidationError

__all__ = ["stdlib"]

_HEX_COLOR_RE = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})")

stdlib = Module(name=None).export_starlark(
    package=__name__,
    resource_name="stdlib.star",
)


@stdlib.export(name="_sys_create_target")
def create_target(ctx: Context, id_: str) -> None:
    with ctx.lock:
        if id_ in ctx.ir.targets:
            msg = f"Duplicate target: {id_}"
            raise ForjeValidationError(msg)

        ctx.ir.targets[id_] = TargetIR(id=id_)


@stdlib.export(name="_sys_target_add_token")
def target_add_token(
    ctx: Context,
    target_id: str,
    token_name: str,
    token_type: str,
    token_mapping: dict[str, str],
) -> None:
    try:
        target = ctx.ir.targets[target_id]
    except LookupError:
        msg = f"Invalid target: {target_id}"
        raise ForjeValidationError(msg) from None

    target.tokens[token_name] = TokenIR(
        name=token_name,
        type_=token_type,
        mapping={k: ValueIR(v) for k, v in token_mapping.items()},
    )


@stdlib.export(name="_sys_color_parse_hex")
def color_parse_hex(value: str) -> tuple[float, float, float, float]:
    if not _HEX_COLOR_RE.fullmatch(value):
        msg = f"Invalid hex color: {value!r}"
        raise ValueError(msg)

    hex_str = value[1:]

    if len(hex_str) in (3, 4):
        hex_str = "".join(c * 2 for c in hex_str)

    if len(hex_str) == 6:
        hex_str = hex_str + "FF"

    r, g, b, a = bytes.fromhex(hex_str)

    return r / 255, g / 255, b / 255, a / 255
