from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from src.app.models.games import Games
from src.app.models.tournament_states import TournamentStates
from src.app.schemas.royale.squad import Squad
from src.app.schemas.royale.stage import StageCreate, StagePreview


class UserData(BaseModel):
    team_name: str
    squad: Optional[Squad]

    class Config:
        orm_mode = True


class TournamentCreate(BaseModel):
    title: str
    description: str
    rewards: List[str]
    stages: List[StageCreate]
    stream_url: str
    game: Games
    max_squads: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]


class TournamentEdit(BaseModel):
    title: Optional[str]
    description: Optional[str]
    stream_url: Optional[str]
    max_squads: Optional[int]
    img_path: Optional[str]
    rewards: Optional[List[str]]


class TournamentAdvancedData(BaseModel):
    id: int
    registered: bool
    can_register: bool


class TournamentPreview(BaseModel):
    id: int
    title: str
    description: str
    stages_count: Optional[int] = Field(default=2)
    start_date: datetime
    end_date: Optional[datetime] = Field(default=None)
    game: Games
    img_path: str
    state: TournamentStates

    class Config:
        orm_mode = True


class Tournament(TournamentPreview):
    stream_url: str
    max_squads: int
    users: List[UserData]
    rewards: List[str]
    stages: List[StagePreview]

    class Config:
        orm_mode = True

