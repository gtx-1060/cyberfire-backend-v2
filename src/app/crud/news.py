from sqlalchemy.orm import Session
from typing import List

from ..schemas import news as news_schemas
from ..models.news import News
from ..exceptions.base import ItemNotFound


def get_news_by_id(news_id: int, db: Session) -> News:
    news = db.query(News).filter(News.id == news_id).first()
    if news is None:
        raise ItemNotFound()
    return news


def get_news(offset: int, count: int, db: Session) -> List[News]:
    news = db.query(News).order_by(News.creation_datetime.desc()) \
        .offset(offset).limit(count).all()
    if news is None:
        return []
    return news


def get_news_count(db: Session) -> int:
    return db.query(News).count()


def create_news(news: news_schemas.NewsCreate, db: Session):
    db_news = News(
        title=news.title,
        text=news.text,
        img_path=""
    )
    db.add(db_news)
    db.commit()


def edit_news(news: news_schemas.NewsEdit, news_id: int, db: Session):
    db_news = get_news_by_id(news_id, db)
    if news.title is not None:
        db_news.title = news.title
    if news.text is not None:
        db_news.text = news.text
    if news.img_path is not None:
        db_news.img_path = news.img_path
    db.add(db_news)
    db.commit()
