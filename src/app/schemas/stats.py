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
    placement: int
    game: Games
    rival_id: int


class MatchStatsEdit(BaseModel):
    kills_count: Optional[int]
    score: Optional[int]
    index: Optional[int]
    placement: Optional[int]


class MatchStats(BaseModel):
    id: int
    score: int
    kills_count: int
    user_data: UserData = Field(..., alias='user')
    index: int
    user_id: int

    class Config:
        orm_mode = True


class LiteMatchStats(BaseModel):
    id: int
    kills_count: int
    placement: int

    class Config:
        orm_mode = True


class TournamentStatsCreate(BaseModel):
    score: int
    kills_count: int
    wins_count: int
    team_name: str


class TournamentStatsEdit(BaseModel):
    score: Optional[int]
    kills_count: Optional[int]
    wins_count: Optional[int]


class TournamentStats(BaseModel):
    score: int
    kills_count: int
    wins_count: int
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