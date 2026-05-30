load("core", "TokenType")

_Role = enum("text", "large_text", "non_text")
_Level = enum("aa", "aaa")

Role = struct(
    Text=_Role("text"),
    LargeText=_Role("large_text"),
    NonText=_Role("non_text"),
)

Level = struct(
    AA=_Level("aa"),
    AAA=_Level("aaa"),
)

AgainstType = record(token=TokenType, role=_Role, level=_Level)


def against(
    token: TokenType,
    *,
    role: _Role = Role.Text,
    level: _Level = Level.AA,
) -> AgainstType:
    token = TokenType(
        name=token.name,
        kind=token.kind,
        context=[],
        mapping=token.mapping,
    )
    return AgainstType(token=token, role=role, level=level)


wcag = struct(
    against=against,
    Role=Role,
    Level=Level,
)
