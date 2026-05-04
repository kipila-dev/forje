__all__ = ["format_elapsed"]


def format_elapsed(seconds: float) -> str:
    if seconds >= 60:
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m}m {s}s"
    if seconds >= 1:
        return f"{seconds:.1f}s"
    return f"{seconds:.3f}s"
