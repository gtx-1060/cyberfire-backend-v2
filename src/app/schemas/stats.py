from typing import Optional
from pydantic import BaseModel

from ..models.games import Games


class MatchStatsCreate(BaseModel):
    kills_count: int
    score: int
    team_name: str
    index: int
    map: str
    game: Games


class MatchStatsEdit(BaseModel):
    kills_count: Optional[int]
    score: Optional[int]
    map: Optional[str]
    attended: Optional[bool]
    index: Optional[int]
    rival_id: Optional[int]
    game: Optional[Games]


class MatchStats(BaseModel):
    id: int
    score: int
    team_name: Optional[str]
    index: int
    squad_id: int


class BattleRoyaleStats(MatchStats):
    kills_count: int


class TvtStats(MatchStats):
    rival_id: int
    map: str


class TournamentStatsCreate(BaseModel):
    score: int
    kills_count: int
    team_name: Optional[str]


class TournamentStatsEdit(BaseModel):
    score: Optional[int]
    kills_count: Optional[int]


class TournamentStats(TournamentStatsCreate):
    squad_id: int


class GlobalStatsCreate(BaseModel):
    score: int
    kills_count: int
    wins_count: int
    team_name: Optional[str]


class GlobalStats(GlobalStatsCreate):
    pass


class GlobalStatsEdit(BaseModel):
    score: Optional[int]
    kills_count: Optional[int]
    wins_count: Optional[int]
