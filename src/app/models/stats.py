from sqlalchemy import Column, ForeignKey, Integer, String, SmallInteger, Enum, Boolean, UniqueConstraint
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
        return Column('user_id', ForeignKey('users.id', ondelete='CASCADE'))

    @declared_attr
    def user(cls):
        return relationship("User")


class MatchStats(StatsMixin, Base):
    __tablename__ = 'match_stats'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lobby_id = Column(Integer, ForeignKey('lobbies.id', ondelete='CASCADE'))
    placement = Column(SmallInteger, default=999)
    index = Column(SmallInteger)
    __table_args__ = (UniqueConstraint('index', 'lobby_id', 'user_id', name='uix_match'),)


class TournamentStats(StatsMixin, Base):
    __tablename__ = 'tournament_stats'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.id', ondelete='CASCADE'))
    wins_count = Column(Integer, default=0)
    __table_args__ = (UniqueConstraint('user_id', name='uix_tournament'),)


class GlobalStats(StatsMixin, Base):
    __tablename__ = 'global_stats'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    wins_count = Column(Integer, default=0)
    __table_args__ = (UniqueConstraint('user_id', 'game', name='uix_globalstats'),)
