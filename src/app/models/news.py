from sqlalchemy import Column, Integer, Text, UnicodeText, TIMESTAMP
from datetime import datetime

from ..config import DEFAULT_IMAGE_PATH
from ..database.db import Base


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(UnicodeText)
    text = Column(UnicodeText)
    creation_datetime = Column(TIMESTAMP, default=datetime.now())
    img_path = Column(Text, default=DEFAULT_IMAGE_PATH)
