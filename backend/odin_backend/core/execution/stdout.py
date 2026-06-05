"""Stdout/stderr ring buffers with stream refs."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class StreamBuffer:
    execution_id: str
    kind: str  # stdout | stderr
    max_lines: int = 2000
    _lines: deque[str] = field(default_factory=deque)
    _lock: Lock = field(default_factory=Lock)

    @property
    def ref(self) -> str:
        return f"{self.execution_id}:{self.kind}"

    def append(self, line: str) -> None:
        with self._lock:
            self._lines.append(line)
            while len(self._lines) > self.max_lines:
                self._lines.popleft()

    def snapshot(self, *, tail: int = 500) -> list[str]:
        with self._lock:
            data = list(self._lines)
        return data[-tail:]

    def text(self, *, tail: int = 500) -> str:
        return "\n".join(self.snapshot(tail=tail))


class StreamBufferRegistry:
    def __init__(self) -> None:
        self._buffers: dict[str, StreamBuffer] = {}

    def get_or_create(self, execution_id: str, kind: str) -> StreamBuffer:
        key = f"{execution_id}:{kind}"
        if key not in self._buffers:
            self._buffers[key] = StreamBuffer(execution_id=execution_id, kind=kind)
        return self._buffers[key]

    def get(self, ref: str) -> StreamBuffer | None:
        return self._buffers.get(ref)

    def drop(self, execution_id: str) -> None:
        for kind in ("stdout", "stderr"):
            self._buffers.pop(f"{execution_id}:{kind}", None)
