from typing import Annotated

import typer

from forje import __version__

app = typer.Typer(
    name="forje",
    help="The build system for your design system.",
    no_args_is_help=True,
    add_completion=False,
)


def version_callback(value: bool):
    if value:
        typer.echo(f"forje {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    _: Annotated[
        bool | None,
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = None,
):
    pass


@app.command()
def build(
    target: Annotated[
        list[str] | None,
        typer.Argument(help="Targets to build. Builds all if omitted."),
    ] = None,
):
    """Build design system resources."""
    if target:
        typer.echo(f"Building target: {target}...")
    else:
        typer.echo("Building all targets...")


@app.command()
def validate():
    """Validate build.forje without executing the build."""
    typer.echo("Validating...")


if __name__ == "__main__":
    app()
