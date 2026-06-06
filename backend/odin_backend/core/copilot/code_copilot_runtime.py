"""Real coding copilot runtime (Prompt 38)."""

from __future__ import annotations

from typing import Any

from odin_backend.core.copilot.code_reasoning.architecture_mapper import map_architecture
from odin_backend.core.copilot.code_reasoning.code_review_engine import review_code
from odin_backend.core.copilot.code_reasoning.code_understanding import understand_code
from odin_backend.core.copilot.code_reasoning.debugging_assistant import suggest_debug_steps
from odin_backend.core.copilot.code_reasoning.dependency_intelligence import analyze_dependencies
from odin_backend.core.copilot.code_reasoning.patch_generator import generate_patch
from odin_backend.core.copilot.code_reasoning.refactor_advisor import advise_refactor
from odin_backend.core.copilot.code_reasoning.repo_reasoner import reason_about_repo


class CodeCopilotRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._patches: list[dict] = []

    async def analyze_repo(self, *, path: str, files: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "code_copilot_enabled", False):
            return {"accepted": False, "reason": "code_copilot_disabled"}
        files = files or []
        reasoning = reason_about_repo(path=path, files=files)
        arch = map_architecture(files=files)
        deps = analyze_dependencies(files=files)
        self._emit("memory_stitched", {"repo": path, "files": len(files)})
        return {"accepted": True, "reasoning": reasoning, "architecture": arch, "dependencies": deps}

    async def debug(self, *, error: str, context: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "code_copilot_enabled", False):
            return {"accepted": False, "reason": "code_copilot_disabled"}
        steps = suggest_debug_steps(error=error, context=context or {})
        return {"accepted": True, **steps}

    async def generate_patch(self, *, file_path: str, goal: str, content: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "code_copilot_enabled", False):
            return {"accepted": False, "reason": "code_copilot_disabled"}
        understanding = understand_code(content=content, path=file_path)
        patch = generate_patch(file_path=file_path, goal=goal, content=content)
        self._patches.append(patch)
        self._emit("code_patch_generated", {"file": file_path, "goal": goal[:80]})
        return {"accepted": True, "understanding": understanding, "patch": patch}

    async def review(self, *, diff: str) -> dict[str, Any]:
        result = review_code(diff=diff)
        return {"accepted": True, **result}

    async def refactor(self, *, file_path: str, smell: str) -> dict[str, Any]:
        advice = advise_refactor(file_path=file_path, smell=smell)
        return {"accepted": True, **advice}

    def snapshot(self) -> dict[str, Any]:
        return {"patches_generated": len(self._patches)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="code_copilot")
