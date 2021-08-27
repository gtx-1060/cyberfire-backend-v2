from typing import List
from pydantic import BaseModel

from src.app.models.tournament_states import StageStates
from src.app.schemas.royale.lobbies import LobbyPreview


class TvtStage(BaseModel):
    id: int
    state: StageStates
    index: int
    matches: List[LobbyPreview]

    class Config:
        orm_mode = True
