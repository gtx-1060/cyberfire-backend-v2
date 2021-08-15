from sqlalchemy import Column, PickleType, Integer, Boolean, UnicodeText, ForeignKey, SmallInteger, TIMESTAMP, Enum
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship, backref

from .tournament_states import StageStates
from ..database.db import Base


class Stage(Base):
    __tablename__ = "stages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    state = Column(Enum(StageStates), default=StageStates.WAITING)
    title = Column(UnicodeText)
    description = Column(UnicodeText)
    kill_leaders = Column(MutableList.as_mutable(PickleType), default=[])
    damage_leaders = Column(MutableList.as_mutable(PickleType), default=[])
    tournament_id = Column(Integer, ForeignKey('tournaments.id', ondelete='CASCADE'))
    lobbies = relationship("Lobby", backref=backref("stage", cascade="all, delete"))
    stage_datetime = Column(TIMESTAMP)
