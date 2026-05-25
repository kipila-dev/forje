_ColorSpace = enum("srgb", "p3")
ColorSpace = struct(
    SRGB=_ColorSpace("srgb"),
    P3=_ColorSpace("p3"),
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
TokenType = record(name=str, kind=_TokenKind, mapping=dict[_Mapping, typing.Any])
ArtifactType = record(
    platform=str,
    path=str,
    stem=field(str | None, default=None),
)


def Color(
    value: str,
    alpha: float | None = None,
    space: _ColorSpace = ColorSpace.SRGB,
) -> ColorType:
    if not isinstance(space, _ColorSpace):
        fail("Invalid argument for 'space': expected a ColorSpace enum")

    if space == ColorSpace.SRGB:
        r, g, b, a = _sys_color_parse_hex(value)
        return ColorType(
            coords=[r, g, b],
            alpha=alpha if alpha != None else a,
            space=space,
        )

    if space == ColorSpace.P3:
        if (
            not isinstance(value, list[float])
            or len(value) != 3
            or min(value) < 0
            or max(value) > 1
        ):
            fail("Invalid argument for 'value': expected a [float, float, float] list")
        return ColorType(
            coords=value,
            alpha=alpha if alpha != None else 1.0,
            space=space,
        )

    fail("Unsupported color space: '{}'.".format(space.value))


def Token(
    name: str,
    value: ColorType | dict[_Mapping, ColorType] | None = None,
    **mapping: dict[str, ColorType],
) -> TokenType:
    if isinstance(value, ColorType):
        return TokenType(
            name=name,
            kind=TokenKind.Color,
            mapping={Mapping.Light: value},
        )

    if isinstance(value, dict[_Mapping, ColorType]):
        return TokenType(
            name=name,
            kind=TokenKind.Color,
            mapping=value,
        )

    if mapping:
        for k in mapping.keys():
            if k not in _Mapping.values():
                fail(
                    "Invalid mapping key '{}'. Supported: {}.".format(
                        k, ", ".join(_Mapping.values())
                    )
                )

        return TokenType(
            name=name,
            kind=TokenKind.Color,
            mapping={_Mapping(k): v for k, v in mapping.items()},
        )

    fail("Token must have a value")


def Artifact(platform: str, path: str, *, stem=None) -> ArtifactType:
    return ArtifactType(platform=platform, path=path, stem=stem)


def target(*, id: str, tokens: list[TokenType], artifacts: list[ArtifactType]) -> None:
    _sys_create_target(id)
    for token in tokens:
        _sys_target_add_token(id, token.name, token.kind, token.mapping)
    for artifact in artifacts:
        _sys_target_add_artifact(id, artifact.platform, artifact.path, artifact.stem)
