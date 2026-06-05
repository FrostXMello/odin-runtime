"""Screenshot capture helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4


def _blank_png() -> bytes:
    try:
        from io import BytesIO

        from PIL import Image

        img = Image.new("RGB", (8, 8), color=(24, 24, 32))
        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception:
        return (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
            b"\x01\x01\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )


def store_snapshot(settings: Any, image_bytes: bytes | None = None, *, suffix: str = ".png") -> str:
    base = Path(getattr(settings, "sandbox_work_dir", Path("./data/sandbox"))) / "screenshots"
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"snap_{uuid4().hex[:12]}{suffix}"
    path.write_bytes(image_bytes if image_bytes else _blank_png())
    return str(path.resolve())
