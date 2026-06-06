from __future__ import annotations


def classify(*, title: str, app: str = "") -> dict:
    kind = "editor"
    t = title.lower()
    if "terminal" in t or app.lower() in ("powershell", "cmd", "iterm"):
        kind = "terminal"
    elif "chrome" in app.lower() or "browser" in t:
        kind = "browser"
    return {"kind": kind, "title": title[:120], "local_only": True}
