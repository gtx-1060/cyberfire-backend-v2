from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from src.app.models.games import Games
from src.app.models.tournament_states import TournamentStates
from src.app.schemas.royale.tournaments import UserData
from src.app.schemas.tvt.stages import TvtStage


class TvtTournamentCreate(BaseModel):
    title: str
    description: str
    rewards: List[str]
    stream_url: str
    game: Games
    max_squads: int
    start_date: datetime


class TvtTournamentEdit(BaseModel):
    title: Optional[str]
    description: Optional[str]
    stream_url: Optional[str]
    max_squads: Optional[int]
    img_path: Optional[str]
    start_date: Optional[datetime]
    rewards: Optional[List[str]]


class TvtTournamentAdvancedData(BaseModel):
    id: int
    registered: bool
    ready_to_play: bool = Field(default=False)
    connect_until: Optional[datetime] = Field(default=None)
    can_register: bool


class TvtTournament(BaseModel):
    id: int
    title: str
    description: str
    start_date: datetime
    game: Games
    img_path: str
    state: TournamentStates
    stream_url: str
    max_squads: int
    users: List[UserData]
    rewards: List[str]
    stages: List[TvtStage]

    class Config:
        orm_mode = True

