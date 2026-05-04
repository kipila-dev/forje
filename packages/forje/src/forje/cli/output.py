import typer

__all__ = ["error", "success"]


def error(message: str) -> None:
    """Prints a formatted error message."""
    typer.secho(f"Error: {message}", fg=typer.colors.RED, err=True)


def success(message: str) -> None:
    """Prints a formatted success message."""
    typer.secho(message, fg=typer.colors.GREEN)
