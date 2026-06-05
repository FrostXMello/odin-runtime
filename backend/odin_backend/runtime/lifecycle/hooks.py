"""Runtime lifecycle hooks."""

from typing import Any, Callable, Awaitable

LifecycleHook = Callable[[], Awaitable[None]]


class LifecycleHooks:
    def __init__(self) -> None:
        self._on_startup: list[LifecycleHook] = []
        self._on_shutdown: list[LifecycleHook] = []

    def on_startup(self, hook: LifecycleHook) -> None:
        self._on_startup.append(hook)

    def on_shutdown(self, hook: LifecycleHook) -> None:
        self._on_shutdown.append(hook)

    async def run_startup(self) -> None:
        for hook in self._on_startup:
            await hook()

    async def run_shutdown(self) -> None:
        for hook in reversed(self._on_shutdown):
            await hook()
