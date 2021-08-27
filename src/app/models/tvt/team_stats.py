from sqlalchemy import Column, ForeignKey, Integer, SmallInteger, Boolean, UniqueConstraint, Text
from sqlalchemy.orm import relationship

from src.app.database.db import Base


class TvtStats(Base):
    __tablename__ = 'tvt_stats'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    score = Column(SmallInteger, nullable=False)
    proof_path = Column(Text, nullable=True)
    confirmed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    user = relationship("User", foreign_keys=[user_id])
    arrival_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    arrival = relationship("User", foreign_keys=[arrival_id])
    match_id = Column(Integer, ForeignKey('tvt_matches.id', ondelete='CASCADE', onupdate='CASCADE'))
    tournament_id = Column(Integer, ForeignKey('tvt_tournaments.id'))
    __table_args__ = (UniqueConstraint('user_id', 'match_id', name='uix_tvtstats1'),
                      UniqueConstraint('arrival_id', 'match_id', name='uix_tvtstats2'),)
