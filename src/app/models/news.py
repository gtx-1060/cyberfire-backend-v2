from sqlalchemy import Column, PickleType, Integer, Text, UnicodeText, TIMESTAMP
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship

from ..database.db import Base


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(UnicodeText),
    text = Column(UnicodeText),
    datetime = Column(TIMESTAMP),
    img_path = Column(Text)
