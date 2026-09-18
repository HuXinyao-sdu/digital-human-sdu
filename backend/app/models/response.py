from pydantic import BaseModel
from typing import List, Optional


class ChatResponse(BaseModel):
    answer: str
    sources: Optional[List[str]] = None
    session_id: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str


class ScriptItem(BaseModel):
    id: int
    title: str
    era: str
    duration: str


class ScriptListResponse(BaseModel):
    total: int
    items: List[ScriptItem]


class PhotoItem(BaseModel):
    id: int
    title: str
    era: str
    location: str
    image_url: str


class GalleryResponse(BaseModel):
    total: int
    items: List[PhotoItem]
