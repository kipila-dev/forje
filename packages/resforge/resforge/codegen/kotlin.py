from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Self

PropertyMutability = Literal["val", "var"]


@dataclass
class KotlinProperty:
    """A single property declaration inside a Kotlin object or file."""

    name: str
    type_: str
    value: str
    mutability: PropertyMutability = "val"

    def render(self) -> str:
        return f"{self.mutability} {self.name}: {self.type_} = {self.value}"


class KotlinObject:
    """A Kotlin object declaration."""

    def __init__(self, name: str) -> None:
        self._name = name
        self._properties: list[KotlinProperty] = []

    def property(
        self,
        name: str,
        type_: str,
        value: str,
        mutability: PropertyMutability = "val",
    ) -> Self:
        self._properties.append(
            KotlinProperty(name=name, type_=type_, value=value, mutability=mutability)
        )
        return self

    def render(self, indent: str = "    ") -> str:
        if not self._properties:
            return f"object {self._name}"
        open_brace = "{"
        lines = [f"object {self._name} {open_brace}"]
        lines.extend(f"{indent}{p.render()}" for p in self._properties)
        lines.append("}")
        return "\n".join(lines)


class KotlinFile:
    """A Kotlin file declaration."""

    def __init__(self, package: str) -> None:
        self._package = package
        self._imports: set[str] = set()
        self._members: list[KotlinProperty | KotlinObject] = []

    def import_(self, fqn: str) -> Self:
        self._imports.add(fqn)
        return self

    def member(self, member: KotlinProperty | KotlinObject) -> Self:
        self._members.append(member)
        return self

    def render(self) -> str:
        sections = [f"package {self._package}"]
        if self._imports:
            sections.append("\n".join(f"import {fqn}" for fqn in sorted(self._imports)))
        sections.extend(m.render() for m in self._members)
        return "\n\n".join(sections) + "\n"

    def write(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            f.write(self.render())
