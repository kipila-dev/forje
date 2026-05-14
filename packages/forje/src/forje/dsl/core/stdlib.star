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

ColorType = record(coords = list[float], alpha = float, space = _ColorSpace)
TokenType = record(name = str, type = str, mapping = dict[_Mapping, ColorType])

def Color(value, space = ColorSpace.SRGB):
    if type(space) != "enum":
        fail("Invalid argument for 'space': expected a ColorSpace enum")
    if space == ColorSpace.SRGB:
        r, g, b, a = _sys_color_parse_hex(value)
        return ColorType(coords = [r, g, b], alpha = a, space = space)
    elif space == ColorSpace.P3:
        return None  # TODO
    else:
        msg = (
            "Unknown color space '{}'. Supported: {}."
        ).format(space, ", ".join(ColorSpace.values()))
        fail(msg)

def ColorToken(name, mapping):
    return TokenType(name = name, type = "color", mapping = mapping)

def target(id, tokens, artifacts):
    _sys_create_target(id)
    for token in tokens:
        _sys_target_add_token(id, token.name, token.type, token.mapping)
