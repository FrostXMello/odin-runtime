"""Speech-to-text via Faster-Whisper (optional dependency)."""

from pathlib import Path

from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class WhisperSTT:
    def __init__(self, model_size: str = "base") -> None:
        self._model_size = model_size
        self._model = None

    def _load(self) -> bool:
        if self._model is not None:
            return True
        try:
            from faster_whisper import WhisperModel

            self._model = WhisperModel(self._model_size, device="cpu", compute_type="int8")
            return True
        except ImportError:
            logger.warning("faster_whisper_not_installed")
            return False

    async def transcribe(self, audio_path: Path) -> str:
        if not self._load():
            return ""
        segments, _ = self._model.transcribe(str(audio_path), beam_size=5)
        return " ".join(s.text for s in segments).strip()
