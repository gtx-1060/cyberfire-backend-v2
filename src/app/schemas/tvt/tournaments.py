from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from src.app.models.games import Games
from src.app.models.tournament_states import TournamentStates
from src.app.schemas.royale.tournaments import UserData
from src.app.schemas.tvt.stages import TvtStage, TvtStageWithAbsent
from src.app.services.tvt.internal_tournament_state import TournamentInternalStateManager


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


class TvtTournamentPreviewPersonal(BaseModel):
    id: int
    registered: bool
    can_register: bool


class MapChoiceRoomData(BaseModel):
    ready_to_connect: bool = False
    connect_until: Optional[datetime] = None


class TvtTournamentPersonal(BaseModel):
    registered: bool
    can_register: bool
    internal_state: TournamentInternalStateManager.State
    in_new_stage: bool = False
    can_load_result_proof: bool = False
    map_choice: MapChoiceRoomData


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
    stages: List[TvtStageWithAbsent]

    class Config:
        orm_mode = True

