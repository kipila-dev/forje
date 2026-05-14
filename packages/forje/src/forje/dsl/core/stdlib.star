_ColorSpace = enum("srgb", "p3")
ColorSpace = struct(
    SRGB = _ColorSpace("srgb"),
    P3 = _ColorSpace("p3"),
)

_Mapping = enum("dark", "light", "high_contrast_dark", "high_contrast_light")
Mapping = struct(
    Dark = _Mapping("dark"),
    Light = _Mapping("light"),
    HighContrastDark = _Mapping("high_contrast_dark"),
    HighContrastLight = _Mapping("high_contrast_light"),
)

_TokenKind = enum("color")
TokenKind = struct(
    Color = _TokenKind("color"),
)

ColorType = record(coords = list[float], alpha = float, space = _ColorSpace)
TokenType = record(name = str, kind = _TokenKind, mapping = dict[_Mapping, typing.Any])

def Color(value, space = ColorSpace.SRGB):
    if not isinstance(space, _ColorSpace):
        fail("Invalid argument for 'space': expected a ColorSpace enum")

    if space == ColorSpace.SRGB:
        r, g, b, a = _sys_color_parse_hex(value)
        return ColorType(coords = [r, g, b], alpha = a, space = space)

    if space == ColorSpace.P3:
        pass  # TODO

    fail("Not implemented")

def Token(name, value = None, **mapping):
    if isinstance(value, ColorType):
        return TokenType(
            name = name,
            kind = TokenKind.Color,
            mapping = {Mapping.Light: value},
        )

    if isinstance(value, dict[_Mapping, ColorType]):
        return TokenType(
            name = name,
            kind = TokenKind.Color,
            mapping = value,
        )

    if mapping:
        for k, v in mapping.items():
            if k not in _Mapping.values():
                msg = (
                    "Invalid mapping key '{}'. Supported: {}."
                ).format(k, ", ".join(_Mapping.values()))
                fail(msg)
            if not isinstance(v, ColorType):
                fail("Invalid mapping value '{}'. Supported: ColorType".format(v))

        return TokenType(
            name = name,
            kind = TokenKind.Color,
            mapping = {_Mapping(k): v for k, v in mapping.items()},
        )

    fail("Invalid token value: {}".format(value))

def target(id, tokens, artifacts):
    _sys_create_target(id)
    for token in tokens:
        _sys_target_add_token(id, token.name, token.kind, token.mapping)
