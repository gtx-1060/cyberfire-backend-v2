from sqlalchemy import Column, ForeignKey, Integer, String, SmallInteger, Enum, Boolean
from sqlalchemy.orm import relationship, declared_attr

from ..database.db import Base
from .games import Games


class StatsMixin(object):
    @declared_attr
    def game(cls):
        return Column(Enum(Games))

    @declared_attr
    def kills_count(cls):
        return Column(Integer, default=0)

    @declared_attr
    def score(cls):
        return Column(Integer, default=0)

    @declared_attr
    def user_id(cls):
        return Column('user_id', ForeignKey('users.id'))

    @declared_attr
    def user(cls):
        return relationship("User")


class MatchStats(StatsMixin, Base):
    __tablename__ = 'match_stats'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    map = Column(String(50), default="")
    stage_id = Column(Integer, ForeignKey('stages.id'))
    rival_id = Column(Integer)
    attended = Column(Boolean, default=True)
    placement = Column(SmallInteger, default=999)
    index = Column(SmallInteger)


class TournamentStats(StatsMixin, Base):
    __tablename__ = 'tournament_stats'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'))
    wins_count = Column(Integer, default=0)


class GlobalStats(StatsMixin, Base):
    __tablename__ = 'global_stats'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    wins_count = Column(Integer, default=0)
