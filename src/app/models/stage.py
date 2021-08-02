from sqlalchemy import Column, PickleType, Integer, Boolean, UnicodeText, ForeignKey, SmallInteger, TIMESTAMP
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship

from ..database.db import Base


class Stage(Base):
    __tablename__ = "stages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    finished = Column(Boolean, default=False)
    title = Column(UnicodeText)
    description = Column(UnicodeText)
    kill_leaders = Column(MutableList.as_mutable(PickleType), default=[])
    damage_leaders = Column(MutableList.as_mutable(PickleType), default=[])
    keys = Column(MutableList.as_mutable(PickleType), default=[])
    teams = Column(MutableList.as_mutable(PickleType), default=[])
    tournament_id = Column(Integer, ForeignKey('tournaments.id'))
    tournament = relationship("Tournament", back_populates="stages")
    matches_count = Column(SmallInteger, default=-1)
    matches = relationship("MatchStats")
    stage_datetime = Column(TIMESTAMP)
