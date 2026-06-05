"""Container execution adapter interface — future Docker/K8s ready."""

from __future__ import annotations

from odin_backend.core.execution.adapters.executor_adapter import (
    DockerAdapter,
    ExecutorAdapter,
    KubernetesAdapter,
    LocalSubprocessAdapter,
    get_executor_adapter,
)

ContainerAdapter = ExecutorAdapter

__all__ = [
    "ContainerAdapter",
    "DockerAdapter",
    "KubernetesAdapter",
    "LocalSubprocessAdapter",
    "get_executor_adapter",
]
