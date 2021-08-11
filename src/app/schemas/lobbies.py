from typing import Optional, List
from pydantic import BaseModel, Field

from src.app.schemas.stats import MatchStats


class LobbyCreate(BaseModel):
    matches_count: int = Field(default=1)
    stage_id: int


class LobbyEdit(BaseModel):
    matches_count: Optional[int]
    key: Optional[str]


class Lobby(LobbyCreate):
    id: int
    stats: List[MatchStats]

    class Config:
        orm_mode = True
