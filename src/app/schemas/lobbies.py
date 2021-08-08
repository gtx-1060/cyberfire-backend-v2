from typing import Optional, List
from pydantic import BaseModel

from src.app.schemas.stats import MatchStats


class LobbyCreate(BaseModel):
    matches_count: int
    teams_count: int


class LobbyEdit(BaseModel):
    matches_count: Optional[int]
    teams_count: Optional[int]
    key: Optional[str]


class Lobby(LobbyCreate):
    id: int
    stats: List[MatchStats]