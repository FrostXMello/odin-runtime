"""Schedule bounded web requests."""

from __future__ import annotations

import asyncio
from typing import Any


class RequestScheduler:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._semaphore = asyncio.Semaphore(getattr(app.settings, "web_max_concurrent", 2))

    async def run(self, coro):
        async with self._semaphore:
            return await coro
