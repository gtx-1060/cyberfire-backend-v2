from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from src.app.models.tournament_states import StageStates
from src.app.schemas.lobbies import Lobby, LobbyCreate


class TournamentData(BaseModel):
    name: str = Field(..., alias='title')

    class Config:
        orm_mode = True


class StageCreate(BaseModel):
    title: str
    description: str
    stage_datetime: datetime
    lobbies: List[LobbyCreate]
    # lobbies_count: int


class StageEdit(BaseModel):
    title: Optional[str]
    description: Optional[str]
    stage_datetime: Optional[datetime]
    kill_leaders: Optional[List[str]]
    damage_leaders: Optional[List[str]]
    lobbies_count: Optional[int]


class Stage(BaseModel):
    id: int
    title: str
    description: str
    stage_datetime: datetime
    kill_leaders: List[str]
    damage_leaders: List[str]
    tournament_data: TournamentData = Field(..., alias='tournament')
    state: StageStates
    lobbies: List[Lobby]
    lobbies_count: int

    key: Optional[str]
    
    class Config:
        orm_mode = True


class StagePreview(BaseModel):
    id: int
    title: str
    stage_datetime: datetime

    class Config:
        orm_mode = True
