MODES = ("minimal", "balanced", "immersive", "cinematic")

def layout(mode: str = "balanced") -> dict:
    m = mode if mode in MODES else "balanced"
    cols = {"minimal": 1, "balanced": 2, "immersive": 3, "cinematic": 4}.get(m, 2)
    return {"mode": m, "columns": cols, "fps_cap": {"minimal": 15, "balanced": 30, "immersive": 45, "cinematic": 60}.get(m, 30)}
