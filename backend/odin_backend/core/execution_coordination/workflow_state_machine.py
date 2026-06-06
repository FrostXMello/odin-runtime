from __future__ import annotations


class WorkflowState:
    def __init__(self, *, workflow_id: str, steps: list[str]) -> None:
        self.workflow_id = workflow_id
        self._steps = steps
        self._index = 0
        self._paused = False

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False
        if self._index < len(self._steps) - 1:
            self._index += 1

    def completed_steps(self) -> list[str]:
        return self._steps[: self._index + 1]
