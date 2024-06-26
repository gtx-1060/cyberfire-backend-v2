from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from src.app.models.games import Games
from src.app.models.tournament_states import StageStates
from src.app.schemas.royale.lobbies import LobbyPreview



class StageUserData(BaseModel):
    team_name: str

    class Config:
        orm_mode = True


class TournamentData(BaseModel):
    name: str = Field(..., alias='title')
    game: Games

    class Config:
        orm_mode = True


class StageCreate(BaseModel):
    title: str
    description: str
    stage_datetime: datetime
    # lobbies_count: int


class StageEdit(BaseModel):
    title: Optional[str]
    description: Optional[str]
    stage_datetime: Optional[datetime]


class StageLeadersEdit(BaseModel):
    damage_leaders: Optional[List[str]] = None
    kill_leaders: Optional[List[str]] = None


class Stage(BaseModel):
    id: int
    title: str
    description: str
    stage_datetime: datetime
    kill_leaders: List[StageUserData]
    damage_leaders: List[StageUserData]
    tournament_data: TournamentData = Field(..., alias='tournament')
    state: StageStates
    lobbies: List[LobbyPreview]
    
    class Config:
        orm_mode = True


class StagePreview(BaseModel):
    id: int
    title: str
    stage_datetime: datetime

    class Config:
        orm_mode = True
