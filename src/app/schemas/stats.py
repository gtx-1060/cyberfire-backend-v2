from typing import Optional
from pydantic import BaseModel, Field

from ..models.games import Games
from ..models import stats as stats_models


class UserData(BaseModel):
    team_name: str

    class Config:
        orm_mode = True


class MatchStatsCreate(BaseModel):
    kills_count: int
    score: int
    team_name: str
    index: int
    map: str
    game: Games
    rival_id: int


class MatchStatsEdit(BaseModel):
    kills_count: Optional[int]
    score: Optional[int]
    map: Optional[str]
    attended: Optional[bool]
    index: Optional[int]
    rival_id: Optional[int]


class MatchStats(BaseModel):
    id: int
    score: int
    user_data: UserData = Field(..., alias='user')
    index: int
    squad_id: int


class BattleRoyaleStats(MatchStats):
    kills_count: int

    class Config:
        orm_mode = True


class TvtStats(MatchStats):
    rival_id: int
    map: str

    class Config:
        orm_mode = True


class TournamentStatsCreate(BaseModel):
    score: int
    kills_count: int
    team_name: str


class TournamentStatsEdit(BaseModel):
    score: Optional[int]
    kills_count: Optional[int]


class TournamentStats(BaseModel):
    score: int
    kills_count: int
    user_data: UserData = Field(..., alias='user')

    class Config:
        orm_mode = True


class GlobalStatsCreate(BaseModel):
    score: int
    kills_count: int
    wins_count: int
    team_name: str


class GlobalStats(BaseModel):
    score: int
    kills_count: int
    wins_count: int
    user_data: UserData = Field(..., alias='user')

    class Config:
        orm_mode = True


class GlobalStatsEdit(BaseModel):
    score: Optional[int]
    kills_count: Optional[int]
    wins_count: Optional[int]