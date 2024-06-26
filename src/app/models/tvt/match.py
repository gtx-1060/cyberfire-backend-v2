from sqlalchemy import Column, ForeignKey, Integer, Boolean, SmallInteger, UniqueConstraint, Text
from sqlalchemy.orm import relationship

from src.app.database.db import Base


class TvtMatch(Base):
    __tablename__ = 'tvt_matches'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    stage_id = Column(Integer, ForeignKey('tvt_stages.id', ondelete='CASCADE'))
    finished = Column(Boolean, default=False)
    index = Column(SmallInteger, nullable=False)
    teams_stats = relationship('TvtStats', cascade="all, delete", backref='match', passive_deletes=True)
    map = Column(Text, nullable=True)
    # absented_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    # absented = relationship('User')
    __table_args__ = (UniqueConstraint('index', 'stage_id', name='uix_tvtmatch'),)
