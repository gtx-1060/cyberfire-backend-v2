from typing import Optional
from pydantic import BaseModel


class UserData(BaseModel):
    team_name: Optional[str]

    class Config:
        orm_mode = True


class TvtStatsPreview(BaseModel):
    id: int
    score: int
    user: Optional[UserData]

    class Config:
        orm_mode = True


class TvtStats(TvtStatsPreview):
    proof_path: Optional[str]
    confirmed: bool

    class Config:
        orm_mode = True


class TvtStatsEdit(BaseModel):
    id: int
    score: int
