from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from src.app.models.games import Games
from src.app.models.tournament_states import States
from src.app.schemas.stage import StageCreate, StagePreview


class TournamentCreate(BaseModel):
    title: str
    description: str
    rewards: List[str]
    stages: List[StageCreate]
    stream_url: str
    game: Games
    max_squads: int


class TournamentEdit(BaseModel):
    title: Optional[str]
    description: Optional[str]
    stream_url: Optional[str]
    max_squads: Optional[int]
    rewards: Optional[str]


class TournamentPreview(BaseModel):
    id: int
    title: str
    description: str
    stages_count: int
    start_date: datetime
    end_date: datetime
    game: Games
    is_player_registered: bool = Field(default=False)
    img_path: str
    state: States


class Tournament(TournamentPreview):
    stream_url: Optional[str]
    max_squads: Optional[int]
    rewards: Optional[str]
    stages: List[StagePreview]

