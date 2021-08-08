from sqlalchemy import Column, PickleType, Integer, UnicodeText, ForeignKey, SmallInteger, Enum, Table, String, Text, \
    TIMESTAMP
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime
from sqlalchemy.orm import relationship, backref

from .games import Games
from ..database.db import Base
from .tournament_states import TournamentStates

association_table = Table('tournament_association', Base.metadata,
                          Column('tournaments_id', Integer, ForeignKey('tournaments.id', ondelete="CASCADE")),
                          Column('users_id', Integer, ForeignKey('users.id', ondelete="CASCADE"))
                          )


class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(UnicodeText)
    description = Column(UnicodeText)
    state = Column(Enum(TournamentStates))
    rewards = Column(MutableList.as_mutable(PickleType))
    stages = relationship("Stage", backref=backref("tournament", cascade="all, delete"))
    users = relationship("User", secondary=association_table, backref="tournaments")
    stages_count = Column(SmallInteger)
    stream_url = Column(String)
    stats = relationship("TournamentStats")  # creates on tournament start
    game = Column(Enum(Games))
    img_path = Column(Text)
    max_squads = Column(SmallInteger)
    start_date = Column(TIMESTAMP, default=datetime.now())
    end_date = Column(TIMESTAMP, default=datetime.now())
