"""Circuit breaker for tools, workflows, and providers."""

import time
from enum import StrEnum

from pydantic import BaseModel, Field


class CircuitState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker(BaseModel):
    name: str
    failure_threshold: int = 5
    recovery_timeout_seconds: float = 60.0
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_at: float | None = None

    def record_success(self) -> None:
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def record_failure(self) -> CircuitState:
        self.failure_count += 1
        self.last_failure_at = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
        return self.state

    def allow_request(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN and self.last_failure_at:
            if time.time() - self.last_failure_at >= self.recovery_timeout_seconds:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        return self.state == CircuitState.HALF_OPEN
