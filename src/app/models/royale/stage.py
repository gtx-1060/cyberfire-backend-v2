from sqlalchemy import Column, PickleType, Integer, Boolean, UnicodeText, ForeignKey, SmallInteger, TIMESTAMP, Enum, \
    Table
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship, backref

from src.app.models.tournament_states import StageStates
from src.app.database.db import Base

kills_association_table = Table('kills_association_table', Base.metadata,
                                Column('stage_id', Integer, ForeignKey('stages.id', ondelete="CASCADE")),
                                Column('users_id', Integer, ForeignKey('users.id', ondelete="CASCADE"))
                                )

damagers_association_table = Table('damagers_association_table', Base.metadata,
                                   Column('stage_id', Integer, ForeignKey('stages.id', ondelete="CASCADE")),
                                   Column('users_id', Integer, ForeignKey('users.id', ondelete="CASCADE"))
                                   )


class Stage(Base):
    __tablename__ = "stages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    state = Column(Enum(StageStates), default=StageStates.WAITING)
    title = Column(UnicodeText)
    description = Column(UnicodeText)
    kill_leaders = relationship("User", secondary=kills_association_table, passive_deletes=True)
    damage_leaders = relationship("User", secondary=damagers_association_table, passive_deletes=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.id', ondelete='CASCADE'))
    lobbies = relationship("Lobby", backref=backref("stage", cascade="all, delete"), passive_deletes=True)
    stage_datetime = Column(TIMESTAMP)
