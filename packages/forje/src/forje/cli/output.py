import typer


def error(message: str) -> None:
    typer.secho(f"Error: {message}", fg=typer.colors.RED, err=True)


def success(message: str) -> None:
    typer.secho(message, fg=typer.colors.GREEN)
