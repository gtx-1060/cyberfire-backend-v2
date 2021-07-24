from sqlalchemy import Column, PickleType, Integer, UnicodeText, ForeignKey, SmallInteger, Enum, Table, String, Text
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship

from .games import Games
from ..database.db import Base
from .tournament_states import States

association_table = Table('tournament_association', Base.metadata,
                          Column('tournaments_id', ForeignKey('tournaments.id'), primary_key=True),
                          Column('users_id', ForeignKey('users.id'), primary_key=True)
                          )


class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(UnicodeText)
    description = Column(UnicodeText)
    state = Column(Enum(States))
    rewards = Column(MutableList.as_mutable(PickleType))
    stages = relationship("Stage", back_populates="tournament", cascade="all,delete")
    users = relationship("User", secondary=association_table, backref="tournaments")
    stages_count = Column(SmallInteger)
    stream_url = Column(String)
    stats = relationship("TournamentStats")
    game = Column(Enum(Games))
    img_path = Column(Text)
    max_squads = Column(SmallInteger)
