from typing import List
from fastapi import APIRouter, Depends, UploadFile
from fastapi.params import File
from sqlalchemy.orm import Session
from starlette.responses import Response

from src.app.schemas.news import NewsCreate, NewsEdit, News
from src.app.services.auth import auth_admin
from src.app.crud import news as news_crud
from src.app.utils import get_db, save_image, delete_image_by_web_path
from ..config import NEWS_STATIC_PATH

router = APIRouter(
    prefix="api/v2/news",
    tags=["news"],
    responses={404: {"description": "Not found"}},
)


@router.post('/')
def create_news(news: NewsCreate, data=Depends(auth_admin), db: Session = Depends(get_db)):
    news_crud.create_news(news, db)
    return Response(status_code=202)


@router.put('/')
def edit_news(news: NewsEdit, news_id: int, data=Depends(auth_admin), db: Session = Depends(get_db)):
    news_crud.edit_news(news, news_id, db)
    return Response(status_code=202)


@router.post('/upload_image')
def upload_news_image(news_id: int, image: UploadFile = File(...), data=Depends(auth_admin),
                      db: Session = Depends(get_db)):
    old_web_path = news_crud.get_news_by_id(news_id, db).img_path
    web_path = save_image(NEWS_STATIC_PATH, image.file.read())
    news_edit = NewsEdit(img_path=web_path)
    news_crud.edit_news(news_edit, news_id, db)
    if old_web_path != '':
        delete_image_by_web_path(old_web_path)
    return Response(status_code=202)


@router.get('/', response_model=List[News])
def get_news(offset=0, count=20, db: Session = Depends(get_db)):
    return news_crud.get_news(offset, count, db)


@router.get('/by_id', response_model=List[News])
def get_news(news_id: int, db: Session = Depends(get_db)):
    return news_crud.get_news_by_id(news_id, db)


@router.get('/count', response_model=int)
def get_news_count(db: Session = Depends(get_db)):
    return news_crud.get_news_count(db)
