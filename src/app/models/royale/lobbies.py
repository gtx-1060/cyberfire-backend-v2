from sqlalchemy import Column, Integer, String, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship

from src.app.database.db import Base


class Lobby(Base):
    __tablename__ = 'lobbies'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    matches_count = Column(SmallInteger)
    stats = relationship("MatchStats", cascade="all, delete", passive_deletes=True)
    key = Column(String(100), default="")
    stage_id = Column(Integer, ForeignKey('stages.id', ondelete='CASCADE'))
