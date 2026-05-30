load(
    "core",
    "Artifact",
    "ArtifactType",
    "Color",
    "ColorSpace",
    "ColorType",
    "Mapping",
    "Token",
    "TokenKind",
    "TokenType",
)


def target(*, id: str, tokens: list[TokenType], artifacts: list[ArtifactType]) -> None:
    _sys_create_target(id)
    for token in tokens:
        _sys_target_add_token(id, token)
    for artifact in artifacts:
        _sys_target_add_artifact(id, artifact)
