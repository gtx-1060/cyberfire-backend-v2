from typing import Optional, List
from pydantic import BaseModel, Field

from src.app.schemas.royale.stats import MatchStats


class LobbyCreate(BaseModel):
    matches_count: int = Field(default=1)
    key: str
    stage_id: int


class LobbyEdit(BaseModel):
    matches_count: Optional[int]
    key: Optional[str]


class LobbyPreview(BaseModel):
    matches_count: int = Field(default=1)
    id: int

    class Config:
        orm_mode = True


class Lobby(LobbyPreview):
    stage_id: int
    key: str
    stats: List[MatchStats]

    class Config:
        orm_mode = True
