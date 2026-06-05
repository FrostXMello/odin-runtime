"""GPU / accelerator monitoring."""

from __future__ import annotations

from typing import Any


def gpu_status() -> dict[str, Any]:
    info: dict[str, Any] = {"gpu_detected": False, "devices": []}
    try:
        import torch

        if torch.cuda.is_available():
            info["gpu_detected"] = True
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                info["devices"].append(
                    {
                        "index": i,
                        "name": props.name,
                        "total_mb": int(props.total_memory / (1024 * 1024)),
                    }
                )
    except Exception:
        pass
    # Apple Silicon hint via platform
    try:
        import platform

        if platform.system() == "Darwin" and platform.machine() == "arm64":
            info["apple_silicon"] = True
    except Exception:
        pass
    return info
