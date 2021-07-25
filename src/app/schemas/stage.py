from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class StageCreate(BaseModel):
    tournament_id: int
    title: str
    description: str
    stage_datetime: datetime
    matches_count: int


class StageEdit(BaseModel):
    tournament_id: Optional[int]
    title: Optional[str]
    description: Optional[str]
    stage_datetime: Optional[datetime]
    matches_count: Optional[int]
    kill_leaders: Optional[List[str]]
    damage_leaders: Optional[List[str]]
    finished: Optional[bool]
    keys: Optional[List[str]]


class Stage(StageCreate):
    kill_leaders: List[str]
    damage_leaders: List[str]
    finished: bool
    keys: List[str]
    
    class Config:
        orm_mode = True
