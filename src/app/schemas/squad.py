from typing import List
from pydantic import BaseModel

from ..models.games import Games


class Squad(BaseModel):
    game: Games
    players: List[str]

    class Config:
        orm_mode = True
