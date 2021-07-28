from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class NewsCreate(BaseModel):
    title: str
    text: str


class NewsEdit(BaseModel):
    title: Optional[str]
    text: Optional[str]
    img_path: Optional[str]


class News(NewsCreate):
    creation_datetime: datetime
    img_path: str

    class Config:
        orm_mode = True
