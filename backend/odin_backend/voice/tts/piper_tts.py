"""Text-to-speech via Piper (optional)."""

import subprocess
from pathlib import Path

from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class PiperTTS:
    def __init__(self, voice_path: str | None = None) -> None:
        self._voice_path = voice_path

    async def synthesize(self, text: str, output_path: Path) -> bool:
        if not self._voice_path:
            logger.debug("piper_not_configured")
            return False
        try:
            proc = subprocess.run(
                ["piper", "--model", self._voice_path, "--output_file", str(output_path)],
                input=text.encode(),
                capture_output=True,
                timeout=30,
            )
            return proc.returncode == 0
        except FileNotFoundError:
            logger.warning("piper_binary_not_found")
            return False
