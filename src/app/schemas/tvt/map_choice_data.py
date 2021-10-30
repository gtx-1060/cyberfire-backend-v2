from datetime import datetime
from typing import List, Tuple, Set
from pydantic import BaseModel

from src.app.models.tournament_states import StageStates
from src.app.schemas.tvt.matches import TvtMatch, TvtMatchShortData


class MapChoiceData(BaseModel):
    teams: Tuple[str, str]
    maps: Set[str]
    active_team: str
    switch_time: datetime
