from forje.dsl import ForjeModule

color = ForjeModule("color")


@color.export
def ramp(name: str) -> dict[str, str]:
    return {}
