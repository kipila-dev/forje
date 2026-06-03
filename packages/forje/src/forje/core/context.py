from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from threading import RLock
from typing import TYPE_CHECKING, final, override

if TYPE_CHECKING:
    from forje.ir import IR

__all__ = ["Context", "context_proxy"]

_ctx: ContextVar[Context] = ContextVar("ctx")


@final
@dataclass
class Context:
    ir: IR
    lock: RLock = field(init=False, default_factory=RLock)


class _ContextProxy:
    def __getattr__(self, name: str) -> object:
        try:
            return getattr(_ctx.get(), name)  # pyright: ignore[reportAny]
        except LookupError as e:
            msg = "No build context active."
            raise RuntimeError(msg) from e

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


context_proxy = _ContextProxy()
