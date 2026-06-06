from __future__ import annotations

def session(*, voice: bool = False, text: bool = True) -> dict:
    return {"modalities": [m for m, on in (("voice", voice), ("text", text)) if on], "unified": True}
