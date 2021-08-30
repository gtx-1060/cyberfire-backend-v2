from typing import List
from pydantic import BaseModel

from src.app.schemas.tvt.team_stats import TvtStatsPreview


class TvtMatch(BaseModel):
    id: int
    finished: bool
    index: int
    teams_stats: List[TvtStatsPreview]

    class Config:
        orm_mode = True


class TvtMatchShortData(BaseModel):
    index: int
    team_name: str
