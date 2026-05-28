_ColorSpace = enum("oklch", "p3", "srgb", "xyz-d65")
ColorSpace = struct(
    OKLCH=_ColorSpace("oklch"),
    P3=_ColorSpace("p3"),
    SRGB=_ColorSpace("srgb"),
    XYZ_D65=_ColorSpace("xyz-d65"),
)

_Mapping = enum("dark", "light", "high_contrast_dark", "high_contrast_light")
Mapping = struct(
    Dark=_Mapping("dark"),
    Light=_Mapping("light"),
    HighContrastDark=_Mapping("high_contrast_dark"),
    HighContrastLight=_Mapping("high_contrast_light"),
)

_TokenKind = enum("color")
TokenKind = struct(
    Color=_TokenKind("color"),
)

ColorType = record(coords=list[float], alpha=float, space=_ColorSpace)
TokenType = record(
    name=str,
    kind=_TokenKind,
    on=typing.Any | None,
    mapping=dict[_Mapping, ColorType],
)
ArtifactType = record(
    platform=str,
    path=str,
    stem=field(str | None, default=None),
)


def Color(
    *value,
    alpha: float | None = None,
    space: _ColorSpace = ColorSpace.SRGB,
) -> ColorType:
    """Creates a color definition.

    Args:
        *value: Either a hex string (e.g., "#FF0000") or three floats
            representing color coordinates (e.g., 1.0, 0.0, 0.0).
        alpha: Optional alpha channel value (0.0 to 1.0). If provided,
            it overrides any alpha parsed from a hex string.
        space: The color space for float inputs. Defaults to SRGB.
    """
    if isinstance(value[0], str):
        r, g, b, a = _sys_color_parse_hex(value[0])
        return ColorType(
            coords=[r, g, b],
            alpha=alpha if alpha != None else a,
            space=ColorSpace.SRGB,
        )

    if (
        len(value) == 3
        and isinstance(value[0], float)
        and isinstance(value[1], float)
        and isinstance(value[2], float)
    ):
        return ColorType(
            coords=[value[0], value[1], value[2]],
            alpha=alpha if alpha != None else 1.0,
            space=space,
        )

    fail("Invalid value: '{}'.".format(value))


def Token(
    name: str,
    value: ColorType | dict[_Mapping, ColorType] | None = None,
    on: TokenType | None = None,
    **mapping: dict[str, ColorType],
) -> TokenType:
    if isinstance(value, ColorType):
        return TokenType(
            name=name,
            kind=TokenKind.Color,
            on=on,
            mapping={Mapping.Light: value},
        )

    if isinstance(value, dict[_Mapping, ColorType]):
        return TokenType(
            name=name,
            kind=TokenKind.Color,
            on=on,
            mapping=value,
        )

    if mapping:
        for k in mapping:
            if k not in _Mapping.values():
                fail(
                    "Invalid mapping key '{}'. Supported: {}.".format(
                        k,
                        ", ".join(_Mapping.values()),
                    ),
                )

        return TokenType(
            name=name,
            kind=TokenKind.Color,
            on=on,
            mapping={_Mapping(k): v for k, v in mapping.items()},
        )

    fail("Token must have a value")


def Artifact(platform: str, path: str, *, stem=None) -> ArtifactType:
    return ArtifactType(platform=platform, path=path, stem=stem)


def target(*, id: str, tokens: list[TokenType], artifacts: list[ArtifactType]) -> None:
    _sys_create_target(id)
    for token in tokens:
        _sys_target_add_token(id, token)
    for artifact in artifacts:
        _sys_target_add_artifact(id, artifact)
