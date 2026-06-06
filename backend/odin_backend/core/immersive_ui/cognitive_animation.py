def animation(*, thinking: bool) -> dict:
    return {"thinking": thinking, "style": "pulse" if thinking else "idle", "gpu_safe": True}
