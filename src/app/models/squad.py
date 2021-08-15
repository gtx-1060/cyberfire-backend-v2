from sqlalchemy import Column, ForeignKey, Integer, Enum, PickleType, Unicode, String
from sqlalchemy.ext.mutable import MutableList

from .games import Games
from ..database.db import Base


class Squad(Base):
    __tablename__ = 'squads'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    game = Column(Enum(Games))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    players = Column(MutableList.as_mutable(PickleType))
