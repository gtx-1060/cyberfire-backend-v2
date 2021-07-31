from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class TournamentData(BaseModel):
    name: str = Field(..., alias='title')

    class Config:
        orm_mode = True


class StageCreate(BaseModel):
    title: str
    description: str
    stage_datetime: datetime
    matches_count: int


class StageEdit(BaseModel):
    title: Optional[str]
    description: Optional[str]
    stage_datetime: Optional[datetime]
    kill_leaders: Optional[List[str]]
    damage_leaders: Optional[List[str]]
    keys: Optional[List[str]]


class Stage(StageCreate):
    id: int
    kill_leaders: List[str]
    damage_leaders: List[str]
    tournament_data: TournamentData = Field(..., alias='tournament')
    finished: bool
    keys: List[str]
    
    class Config:
        orm_mode = True


class StagePreview(BaseModel):
    id: int
    title: str
    time: datetime

    class Config:
        orm_mode = True
