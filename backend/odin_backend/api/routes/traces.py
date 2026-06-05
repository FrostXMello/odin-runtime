"""Causal trace API."""

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/traces", tags=["traces"])


@router.get("/{trace_id}")
async def get_trace(trace_id: str, request: Request) -> dict:
    app = request.app.state.odin
    data = app.observability.tracer.get_trace(trace_id)
    if not data:
        raise HTTPException(status_code=404, detail="Trace not found")
    return data
