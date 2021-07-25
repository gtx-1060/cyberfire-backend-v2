from sqlalchemy import Column, PickleType, Integer, Boolean, UnicodeText, ForeignKey, SmallInteger, TIMESTAMP
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship

from ..database.db import Base


class Stage(Base):
    __tablename__ = "stages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_team_names = Column(MutableList.as_mutable(PickleType))
    finished = Column(Boolean)
    title = Column(UnicodeText)
    description = Column(UnicodeText)
    kill_leaders = Column(MutableList.as_mutable(PickleType))
    damage_leaders = Column(MutableList.as_mutable(PickleType))
    keys = Column(MutableList.as_mutable(PickleType))
    tournament_id = Column(Integer, ForeignKey('tournaments.id'))
    tournament = relationship("Tournament", back_populates="stages")
    matches_count = Column(SmallInteger, default=-1)
    matches = relationship("MatchStats")
    stage_datetime = Column(TIMESTAMP)
