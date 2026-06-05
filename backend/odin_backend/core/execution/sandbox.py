"""Local-first execution sandbox — no Docker."""

from __future__ import annotations

import os
import re
import shlex
from pathlib import Path

from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

_DANGEROUS_PATTERNS = [
    re.compile(r"\brm\s+-rf\b", re.I),
    re.compile(r"\bformat\b", re.I),
    re.compile(r"\bdel\s+/[fq]", re.I),
    re.compile(r"\|\s*sh\b", re.I),
    re.compile(r"\|\s*bash\b", re.I),
    re.compile(r"\bsudo\b", re.I),
    re.compile(r"\bchmod\s+777\b", re.I),
    re.compile(r"\bmkfs\b", re.I),
    re.compile(r"\bdd\s+if=", re.I),
    re.compile(r">\s*/dev/", re.I),
    re.compile(r"\$\(", re.I),
    re.compile(r"`", re.I),
    re.compile(r";\s*rm\b", re.I),
]

_SHELL_ALLOWLIST_PREFIXES = (
    "echo ",
    "dir ",
    "type ",
    "python ",
    "py ",
    "pip list",
    "where ",
    "whoami",
    "pwd",
    "cd ",
    "ls ",
    "cat ",
    "head ",
    "tail ",
)


class SandboxViolation(Exception):
    pass


class ExecutionSandbox:
    def __init__(self, work_dir: Path) -> None:
        self.work_dir = work_dir.resolve()
        self.work_dir.mkdir(parents=True, exist_ok=True)

    def workspace_for(self, execution_id: str) -> Path:
        path = (self.work_dir / execution_id).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    def validate_shell_command(self, command: str) -> None:
        cmd = command.strip()
        if not cmd:
            raise SandboxViolation("empty command")
        for pat in _DANGEROUS_PATTERNS:
            if pat.search(cmd):
                raise SandboxViolation(f"blocked dangerous pattern: {pat.pattern}")
        lowered = cmd.lower()
        if not any(lowered.startswith(p) for p in _SHELL_ALLOWLIST_PREFIXES):
            raise SandboxViolation(
                "command not in safe allowlist prefix (use echo, python, dir, type, etc.)"
            )

    def resolve_path(self, workspace: Path, relative: str) -> Path:
        target = (workspace / relative).resolve()
        if not str(target).startswith(str(workspace.resolve())):
            raise SandboxViolation("path traversal blocked")
        return target

    def validate_python_source(self, source: str) -> None:
        blocked = ("import os", "import subprocess", "import shutil", "__import__", "eval(", "exec(")
        low = source.lower()
        for token in blocked:
            if token in low:
                raise SandboxViolation(f"blocked python construct: {token}")

    def cleanup_workspace(self, execution_id: str) -> None:
        path = self.work_dir / execution_id
        if path.exists() and path.is_dir():
            for child in path.iterdir():
                try:
                    if child.is_file():
                        child.unlink()
                except OSError as exc:
                    logger.debug("sandbox_cleanup_skip", path=str(child), error=str(exc))
