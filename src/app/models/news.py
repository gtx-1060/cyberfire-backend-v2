from sqlalchemy import Column, Integer, Text, UnicodeText, TIMESTAMP


from ..database.db import Base


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(UnicodeText),
    text = Column(UnicodeText),
    creation_datetime = Column(TIMESTAMP),
    img_path = Column(Text)
