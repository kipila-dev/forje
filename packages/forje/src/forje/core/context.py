from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import TYPE_CHECKING, override

if TYPE_CHECKING:
    from forje.core.ir import IR

__all__ = ["Context", "ContextProxy"]

_ctx: ContextVar[Context] = ContextVar("ctx")


@dataclass
class Context:
    ir: IR


class ContextProxy:
    def __getattr__(self, name: str) -> object:
        try:
            return getattr(_ctx.get(), name)  # pyright: ignore[reportAny]
        except LookupError:
            msg = "No build context active."
            raise RuntimeError(msg) from LookupError

    @override
    def __repr__(self) -> str:
        try:
            return repr(_ctx.get())
        except LookupError:
            return "<empty build context proxy>"

    @classmethod
    def set_context(cls, ctx: Context) -> Token[Context]:
        """Sets the current context."""
        return _ctx.set(ctx)

    @classmethod
    def reset_context(cls, token: Token[Context]) -> None:
        """Resets the context to the state before set_context was called."""
        _ctx.reset(token)
