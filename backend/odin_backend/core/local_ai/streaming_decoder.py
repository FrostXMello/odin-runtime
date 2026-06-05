"""Streaming token callback support."""

from __future__ import annotations

from typing import Any, Callable, Awaitable


class StreamingDecoder:
    def __init__(self) -> None:
        self._tokens: list[str] = []
        self._callbacks: list[Callable[[str], Awaitable[None] | None]] = []

    def on_token(self, cb: Callable[[str], Awaitable[None] | None]) -> None:
        self._callbacks.append(cb)

    async def emit(self, token: str) -> None:
        self._tokens.append(token)
        for cb in self._callbacks:
            result = cb(token)
            if hasattr(result, "__await__"):
                await result

    def text(self) -> str:
        return "".join(self._tokens)
