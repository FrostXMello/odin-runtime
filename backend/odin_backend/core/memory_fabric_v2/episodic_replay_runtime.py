from __future__ import annotations


def replay(*, session: str) -> dict:
    return {"session": session[:80], "replayable": True}
