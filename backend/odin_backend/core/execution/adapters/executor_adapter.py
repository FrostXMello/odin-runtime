"""Container execution adapter interface — future Docker/K8s ready."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator


class ExecutorAdapter(ABC):
    @abstractmethod
    async def start(self, *, execution_id: str, spec: dict[str, Any]) -> dict[str, Any]: ...

    @abstractmethod
    async def stop(self, *, execution_id: str, reason: str = "stop") -> bool: ...

    @abstractmethod
    async def stream_logs(self, execution_id: str) -> AsyncIterator[str]: ...

    @abstractmethod
    async def copy_workspace(self, execution_id: str, dest: str) -> bool: ...

    @abstractmethod
    async def health(self) -> dict[str, Any]: ...


class LocalSubprocessAdapter(ExecutorAdapter):
    """Current behavior — in-process/subprocess via ExecutionEngine."""

    async def start(self, *, execution_id: str, spec: dict[str, Any]) -> dict[str, Any]:
        return {"execution_id": execution_id, "adapter": "local_subprocess", "started": True}

    async def stop(self, *, execution_id: str, reason: str = "stop") -> bool:
        return True

    async def stream_logs(self, execution_id: str):
        if False:
            yield ""
        return

    async def copy_workspace(self, execution_id: str, dest: str) -> bool:
        return True

    async def health(self) -> dict[str, Any]:
        return {"status": "healthy", "adapter": "local_subprocess"}


class DockerAdapter(ExecutorAdapter):
    """Placeholder for future Docker integration."""

    async def start(self, *, execution_id: str, spec: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("DockerAdapter not implemented")

    async def stop(self, *, execution_id: str, reason: str = "stop") -> bool:
        raise NotImplementedError("DockerAdapter not implemented")

    async def stream_logs(self, execution_id: str):
        if False:
            yield ""
        raise NotImplementedError("DockerAdapter not implemented")

    async def copy_workspace(self, execution_id: str, dest: str) -> bool:
        raise NotImplementedError("DockerAdapter not implemented")

    async def health(self) -> dict[str, Any]:
        return {"status": "unavailable", "adapter": "docker"}


class KubernetesAdapter(ExecutorAdapter):
    """Placeholder for future Kubernetes integration."""

    async def start(self, *, execution_id: str, spec: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("KubernetesAdapter not implemented")

    async def stop(self, *, execution_id: str, reason: str = "stop") -> bool:
        raise NotImplementedError("KubernetesAdapter not implemented")

    async def stream_logs(self, execution_id: str):
        if False:
            yield ""
        raise NotImplementedError("KubernetesAdapter not implemented")

    async def copy_workspace(self, execution_id: str, dest: str) -> bool:
        raise NotImplementedError("KubernetesAdapter not implemented")

    async def health(self) -> dict[str, Any]:
        return {"status": "unavailable", "adapter": "kubernetes"}


def get_executor_adapter(kind: str = "local") -> ExecutorAdapter:
    if kind == "docker":
        return DockerAdapter()
    if kind == "kubernetes":
        return KubernetesAdapter()
    return LocalSubprocessAdapter()
