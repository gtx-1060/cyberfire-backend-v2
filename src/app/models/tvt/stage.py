from sqlalchemy import Column, Integer, UnicodeText, ForeignKey, Enum, SmallInteger, Table
from sqlalchemy.orm import relationship, backref

from src.app.models.tournament_states import StageStates
from src.app.database.db import Base

suspended_association_table = Table('suspended_association_table', Base.metadata,
                                    Column('stage_id', Integer, ForeignKey('stages.id', ondelete="CASCADE")),
                                    Column('users_id', Integer, ForeignKey('users.id', ondelete="CASCADE"))
                                    )


class TvtStage(Base):
    __tablename__ = "tvt_stages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    state = Column(Enum(StageStates), default=StageStates.WAITING)
    tournament_id = Column(Integer, ForeignKey('tvt_tournaments.id', ondelete='CASCADE'))
    index = Column(SmallInteger, default=0)
    matches = relationship("TvtMatch", backref=backref("stage", cascade="all, delete"), passive_deletes=True)
    absent_users = relationship("User", secondary=suspended_association_table, passive_deletes=True)
