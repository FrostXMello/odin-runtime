"""Cancellation tokens for running executions."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field


@dataclass
class CancellationToken:
    execution_id: str
    _event: asyncio.Event = field(default_factory=asyncio.Event)

    def cancel(self) -> None:
        self._event.set()

    @property
    def is_cancelled(self) -> bool:
        return self._event.is_set()

    async def wait_cancelled(self) -> None:
        await self._event.wait()


class CancellationRegistry:
    def __init__(self) -> None:
        self._tokens: dict[str, CancellationToken] = {}
        self._tasks: dict[str, asyncio.Task] = {}

    def register(self, execution_id: str) -> CancellationToken:
        tok = CancellationToken(execution_id=execution_id)
        self._tokens[execution_id] = tok
        return tok

    def bind_task(self, execution_id: str, task: asyncio.Task) -> None:
        self._tasks[execution_id] = task

    def cancel(self, execution_id: str) -> bool:
        tok = self._tokens.get(execution_id)
        if tok:
            tok.cancel()
        task = self._tasks.get(execution_id)
        if task and not task.done():
            task.cancel()
            return True
        return tok is not None

    def drop(self, execution_id: str) -> None:
        self._tokens.pop(execution_id, None)
        self._tasks.pop(execution_id, None)
