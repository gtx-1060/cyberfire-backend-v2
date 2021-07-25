from typing import Optional
from pydantic import BaseModel

from ..models.games import Games


class MatchStatsCreate(BaseModel):
    kills_count: int
    wins_count: int
    score: int
    team_name: str
    game: Games


class MatchStatsEdit(BaseModel):
    kills_count: Optional[int]
    wins_count: Optional[int]
    score: Optional[int]
    team_name: Optional[str]

