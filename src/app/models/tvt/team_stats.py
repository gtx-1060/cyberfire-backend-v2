from sqlalchemy import Column, ForeignKey, Integer, SmallInteger, Boolean, UniqueConstraint, Text
from sqlalchemy.orm import relationship

from src.app.config import DEFAULT_PROOF_PATH
from src.app.database.db import Base


class TvtStats(Base):
    __tablename__ = 'tvt_stats'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    score = Column(SmallInteger, nullable=False, default=0)
    proof_path = Column(Text, default=DEFAULT_PROOF_PATH)
    confirmed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    user = relationship("User", foreign_keys=[user_id])
    rival_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    rival = relationship("User", foreign_keys=[rival_id])
    match_id = Column(Integer, ForeignKey('tvt_matches.id', ondelete='CASCADE', onupdate='CASCADE'))
    tournament_id = Column(Integer, ForeignKey('tvt_tournaments.id', ondelete='CASCADE'))
    __table_args__ = (UniqueConstraint('user_id', 'match_id', name='uix_tvtstats1'),
                      UniqueConstraint('rival_id', 'match_id', name='uix_tvtstats2'),)
