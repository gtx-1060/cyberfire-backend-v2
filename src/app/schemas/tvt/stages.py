from typing import List, Optional
from pydantic import BaseModel

from src.app.models.tournament_states import StageStates
from src.app.schemas.tvt.matches import TvtMatch, TvtMatchShortData


class TvtStage(BaseModel):
    id: int
    state: StageStates
    index: int
    matches: List[TvtMatch]

    class Config:
        orm_mode = True


class AdminsManagementData(BaseModel):
    stage: TvtStage
    skipped: Optional[TvtMatchShortData]
    kicked_teams: List[str]
