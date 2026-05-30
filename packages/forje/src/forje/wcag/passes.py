from collections.abc import Generator
from typing import override

import coloraide
from pydantic import ValidationError

from forje.core.driver import Pass
from forje.core.errors import ForjeValidationError
from forje.ir import IR, ColorNode, TokenMapping, TokenNode
from forje.passes.color_norm import normalize_token_node
from forje.wcag.models import AgainstNode, Level, Role, against_adapter

_WCAG_THRESHOLDS: dict[tuple[Role, Level], float] = {
    ("text", "aa"): 4.5,
    ("text", "aaa"): 7.0,
    ("large_text", "aa"): 3.0,
    ("large_text", "aaa"): 4.5,
    ("non_text", "aa"): 3.0,
    ("non_text", "aaa"): 3.0,
}


def _resolve_wcag_nodes(context: list[object]) -> Generator[AgainstNode]:
    for node in context:
        if isinstance(node, AgainstNode):
            yield node
            continue
        try:
            against_node = against_adapter.validate_python(node)
            against_node.token = normalize_token_node(against_node.token)
            yield against_node
        except ValidationError:
            continue


def _walk_wcag_tokens(ir: IR) -> Generator[tuple[TokenNode, list[AgainstNode]]]:
    for target in ir.targets.values():
        for token in target.tokens.values():
            wcag_nodes = list(_resolve_wcag_nodes(token.context))
            if wcag_nodes:
                yield token, wcag_nodes


def _expand_mapping(
    mapping: dict[TokenMapping, ColorNode],
) -> dict[TokenMapping, ColorNode]:
    light = mapping["light"]
    dark = mapping.get("dark", light)
    return {
        "light": light,
        "dark": dark,
        "high_contrast_light": mapping.get("high_contrast_light", light),
        "high_contrast_dark": mapping.get("high_contrast_dark", dark),
    }


def _make_coloraide_color(node: ColorNode) -> coloraide.Color:
    return coloraide.Color("xyz-d65", node.coords, node.alpha)


def _validate_contrast(
    token: TokenNode,
    against: AgainstNode,
) -> list[ForjeValidationError]:
    errors: list[ForjeValidationError] = []

    variants = token.mapping.keys() | against.token.mapping.keys()
    token_expanded = _expand_mapping(token.mapping)
    against_expanded = _expand_mapping(against.token.mapping)
    token_mapping = {k: v for k, v in token_expanded.items() if k in variants}
    against_mapping = {k: v for k, v in against_expanded.items() if k in variants}
    required_contrast = _WCAG_THRESHOLDS[(against.role, against.level)]

    for variant in variants:
        token_color = _make_coloraide_color(token_mapping[variant])
        against_color = _make_coloraide_color(against_mapping[variant])
        contrast_ratio = token_color.contrast(against_color, "wcag21")

        if contrast_ratio < required_contrast:
            msg = (
                f"WCAG {against.level.upper()} contrast failure "
                f"({against.role}, {variant}): "
                f"'{token.name}' vs '{against.token.name}' "
                f"is {contrast_ratio:.2f}:1, requires ≥ {required_contrast:.1f}:1"
            )
            errors.append(ForjeValidationError(msg))

    return errors


class WCAGValidation(Pass):
    @override
    def run(self, ir: IR) -> None:
        errors: list[ForjeValidationError] = []

        for token, wcag_nodes in _walk_wcag_tokens(ir):
            for node in wcag_nodes:
                errors.extend(_validate_contrast(token, node))

        if errors:
            msg = "WCAG validation failed"
            raise ExceptionGroup(msg, errors)
