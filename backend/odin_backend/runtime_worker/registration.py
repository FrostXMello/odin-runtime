"""Worker registration and capability advertisement."""

from __future__ import annotations

from typing import Any

from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class WorkerRegistration:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def register(
        self,
        *,
        role: str = "execution",
        capabilities: list[str] | None = None,
    ) -> None:
        reg = self._app.worker_registry
        caps = capabilities or list(reg.capabilities)
        if role == "execution" and "mission_dispatch" not in caps:
            caps = ["mission_dispatch", *caps]
        await reg.register(capabilities=caps)
        logger.info("worker_registered", worker_id=reg.worker_id, role=role, capabilities=caps)
