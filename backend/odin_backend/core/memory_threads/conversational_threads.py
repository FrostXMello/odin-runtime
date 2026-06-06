from __future__ import annotations

def conv_thread(*, thread_id: str) -> dict:
    return {"thread_id": thread_id, "kind": "conversation"}
