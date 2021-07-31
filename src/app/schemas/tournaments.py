from typing import Optional, List
from pydantic import BaseModel, Field

from src.app.models.games import Games
from src.app.models.tournament_states import States
from src.app.schemas.stage import StageCreate


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


class Tournament(TournamentCreate):
    id: int
    state: States
    img_path: str
    is_player_registered: bool = Field(default=False)
