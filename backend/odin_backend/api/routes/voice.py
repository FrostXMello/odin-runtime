"""Voice API — push-to-talk foundation."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/voice", tags=["voice"])


class VoiceSpeakRequest(BaseModel):
    text: str


@router.post("/sessions")
async def start_voice_session(request: Request) -> dict:
    app = request.app.state.odin
    if not app.voice.enabled:
        raise HTTPException(status_code=403, detail="Voice disabled — set ODIN_VOICE_ENABLED=true")
    session = await app.voice.start_session(push_to_talk=True)
    return session.model_dump(mode="json")


@router.post("/sessions/{session_id}/speak")
async def speak(session_id: str, body: VoiceSpeakRequest, request: Request) -> dict:
    app = request.app.state.odin
    ok = await app.voice.speak(session_id, body.text)
    return {"success": ok, "session_id": session_id}
