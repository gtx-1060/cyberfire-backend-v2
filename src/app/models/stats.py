from sqlalchemy import Column, ForeignKey, Integer, String, SmallInteger, Enum
from sqlalchemy.orm import relationship

from ..database.db import Base
from .games import Games


class Stats:
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    game = Column(Enum(Games))
    kills_count = Column(Integer)
    wins_count = Column(Integer)
    score = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User")
    squad_id = Column(Integer, ForeignKey('squads.id'))


class MatchStats(Stats, Base):
    __tablename__ = 'match_stats'

    map = Column(String(50))

    stage_id = Column(Integer, ForeignKey('stages.id'))
    index = Column(SmallInteger)


class TournamentStats(Stats, Base):
    __tablename__ = 'tournament_stats'

    tournament_id = Column(Integer, ForeignKey('tournaments.id'))


class GlobalStats(Stats, Base):
    __tablename__ = 'global_stats'
