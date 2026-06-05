"""HEIMDALL permission API."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/permissions", tags=["permissions"])


class ApproveRequest(BaseModel):
    request_id: str


@router.get("/pending")
async def list_pending(request: Request) -> list[dict]:
    app = request.app.state.odin
    return [r.model_dump(mode="json") for r in app.heimdall.list_pending()]


@router.post("/approve")
async def approve_permission(body: ApproveRequest, request: Request) -> dict:
    app = request.app.state.odin
    req = await app.heimdall.approve(body.request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Permission request not found")
    return req.model_dump(mode="json")
