import logging
import time
from pathlib import Path
from typing import Annotated

import typer
from rich import print
from rich.logging import RichHandler

import forje.core.compiler
from forje import __version__
from forje.cli.ui import error, success
from forje.cli.utils import format_elapsed
from forje.core.environment import Environment
from forje.errors import ForjeEvalError, ForjeParseError, ForjePluginLoadError

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

app = typer.Typer(
    name="forje",
    no_args_is_help=True,
    add_completion=False,
)


def _find_build_file() -> Path | None:
    candidate = Path.cwd() / "build.forje"
    return candidate if candidate.exists() else None


def _version_callback(*, value: bool) -> None:
    if value:
        print(f"forje {__version__}")
        raise typer.Exit


@app.callback()
def main(
    _: Annotated[
        bool | None,
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = None,
) -> None:
    """Build design system resources from Starlark definitions."""


@app.command()
def build() -> None:
    """Build design system resources."""
    build_file = _find_build_file()

    if build_file is None:
        error("build.forje not found in current directory.")
        raise typer.Exit(code=1)

    try:
        source = build_file.read_text(encoding="utf-8")
    except OSError as e:
        error(f"Could not read build.forje: {e.strerror}")
        raise typer.Exit(code=1) from e

    start = time.perf_counter()

    try:
        env = Environment().load_plugins()
        ir = forje.core.compiler.run_build(env, source)
        print(ir)
    except (ForjePluginLoadError, ForjeParseError, ForjeEvalError) as e:
        error(str(e))
        raise typer.Exit(code=1) from e

    elapsed = time.perf_counter() - start
    success(f"Build succeeded in {format_elapsed(elapsed)}")


if __name__ == "__main__":
    app()
