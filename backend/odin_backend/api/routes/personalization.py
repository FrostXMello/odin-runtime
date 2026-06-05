"""Personalization API."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/personalization", tags=["personalization"])


class ProfileUpdate(BaseModel):
    tone: str | None = None
    research_depth: str | None = None
    summarization_style: str | None = None


@router.get("/profile")
async def get_profile(request: Request) -> dict:
    app = request.app.state.odin
    profile = await app.personalization.load()
    return profile.model_dump()


@router.patch("/profile")
async def update_profile(body: ProfileUpdate, request: Request) -> dict:
    app = request.app.state.odin
    app.personalization.update_preference(**body.model_dump(exclude_none=True))
    await app.personalization.save()
    return (await app.personalization.load()).model_dump()
