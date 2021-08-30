from sqlalchemy import Column, PickleType, Integer, UnicodeText, ForeignKey, SmallInteger, Enum, Table, String, Text, \
    TIMESTAMP
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime
from sqlalchemy.orm import relationship, backref

from src.app.models.games import Games
from src.app.database.db import Base
from src.app.models.tournament_states import TournamentStates

association_table = Table('tvt_tournament_association', Base.metadata,
                          Column('tournaments_id', Integer, ForeignKey('tvt_tournaments.id', ondelete="CASCADE")),
                          Column('users_id', Integer, ForeignKey('users.id', ondelete="CASCADE"))
                          )


class TvtTournament(Base):
    __tablename__ = "tvt_tournaments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(UnicodeText)
    description = Column(UnicodeText)
    state = Column(Enum(TournamentStates))
    rewards = Column(MutableList.as_mutable(PickleType))
    stages = relationship("TvtStage", backref=backref("tournament", cascade="all, delete"), passive_deletes=True)
    users = relationship("User", secondary=association_table, backref="tvt_tournaments")
    stream_url = Column(String)
    game = Column(Enum(Games))
    img_path = Column(Text)
    max_squads = Column(SmallInteger)
    start_date = Column(TIMESTAMP, default=datetime.now())
