from sqlalchemy import Boolean, Column, Integer, Unicode, TIMESTAMP, Text, Enum, String
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database.db import Base
from .roles import Roles


class User(Base):
    __tablename__ = 'users'

    # есть поле tournaments, сгенерированное backref'ом

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(Unicode(100), unique=True, index=True)
    team_name = Column(String(100), unique=True, index=True)
    refresh_token = Column(Text)
    username = Column(Unicode(50))
    squads = Column(relationship('Squad', cascade="all,delete"))
    avatar_path = Column(Text)  # default value needed
    hashed_password = Column(Unicode(200))
    is_active = Column(Boolean, default=True)
    is_confirmed = Column(Boolean, default=False)
    registration_date = Column(TIMESTAMP, default=datetime.now())
    role = Column(Enum(Roles), default=Roles.USER)
