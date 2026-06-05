"""Standalone distributed worker process entrypoint."""

from __future__ import annotations

import argparse
import asyncio
import signal
from typing import Any

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.runtime.workers import new_worker_id
from odin_backend.monitoring.logging import configure_logging, get_logger
from odin_backend.runtime_worker.execution_worker import ExecutionWorker
from odin_backend.runtime_worker.planner_worker import PlannerWorker
from odin_backend.runtime_worker.recovery_worker import RecoveryWorker

logger = get_logger(__name__)


async def run_worker(
    *,
    worker_type: str = "execution",
    worker_id: str | None = None,
    settings: Settings | None = None,
) -> None:
    settings = settings or Settings()
    settings.worker_id = worker_id or settings.worker_id or new_worker_id(worker_type)
    settings.queue_persist_enabled = True
    configure_logging(settings)

    app = OdinApplication(settings, use_redis=settings.queue_backend == "redis")
    await app.startup()

    workers: dict[str, Any] = {
        "execution": ExecutionWorker(app),
        "planner": PlannerWorker(app),
        "recovery": RecoveryWorker(app),
    }
    worker = workers.get(worker_type, ExecutionWorker(app))
    stop = asyncio.Event()

    def _handle_sig(*_: Any) -> None:
        stop.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _handle_sig)
        except NotImplementedError:
            pass

    await worker.start()
    logger.info("worker_started", worker_type=worker_type, worker_id=settings.worker_id)
    try:
        await stop.wait()
    finally:
        await worker.stop()
        await app.shutdown()


def main() -> None:
    parser = argparse.ArgumentParser(description="Odin distributed runtime worker")
    parser.add_argument("--type", choices=["execution", "planner", "recovery"], default="execution")
    parser.add_argument("--worker-id", default=None)
    args = parser.parse_args()
    asyncio.run(run_worker(worker_type=args.type, worker_id=args.worker_id))


if __name__ == "__main__":
    main()
