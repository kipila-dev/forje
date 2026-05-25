# Forje

**A build system for your design system.**

Define your design tokens once, compile to native artifacts automatically. Build
scripts are written in [Starlark](https://bazel.build/rules/language), the same
language used by Bazel and Buck2.

```starlark
# build.forje
target(
    id="acme",
    tokens=[
        Token("primary", Color("#38BDF8")),
        Token(
            "surface",
            dark=Color("#0F172A"),
            light=Color("#FFFFFF"),
        ),
    ],
    artifacts=[
        Artifact("android", "acme/res"),
        Artifact("apple", "acme", stem="Assets"),
    ],
)
```

## Installation

```sh
pip install forje
```

Requires Python 3.12+.

## Usage

Create a `build.forje` in your project root and run:

```sh
forje build
```

## Extending Forje

Plugins expose new DSL functions and backends via Python entry points.

**New DSL extension:**

```toml
[project.entry-points."forje.dsl"]
myplugin = "myplugin.dsl:myplugin_module"
```

**New platform backend:**

```toml
[project.entry-points."forje.backend"]
myplatform = "myplugin.backend.myplatform:MyPlatformBackend"
```

## License

MIT
