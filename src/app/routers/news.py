from typing import List
from fastapi import APIRouter, Depends, UploadFile
from fastapi.params import File
from sqlalchemy.orm import Session
from starlette.responses import Response

from src.app.schemas.news import NewsCreate, NewsEdit, News
from src.app.services.auth_service import auth_admin
from src.app.crud import news as news_crud
from src.app.utils import get_db, save_image, delete_image_by_web_path
from ..config import NEWS_STATIC_PATH

router = APIRouter(
    prefix="/api/v2/news",
    tags=["news"],
    responses={404: {"description": "Not found"}},
)


@router.post('', response_model=dict)
def create_news(news: NewsCreate, _=Depends(auth_admin), db: Session = Depends(get_db)):
    news_id = news_crud.create_news(news, db).id
    return {'id': news_id}


@router.put('')
def edit_news(news: NewsEdit, news_id: int, _=Depends(auth_admin), db: Session = Depends(get_db)):
    news_crud.edit_news(news, news_id, db)
    return Response(status_code=202)


@router.post('/upload_image')
def upload_news_image(news_id: int, image: UploadFile = File(...), _=Depends(auth_admin),
                      db: Session = Depends(get_db)):
    old_web_path = news_crud.get_news_by_id(news_id, db).img_path
    web_path = save_image(NEWS_STATIC_PATH, image.file.read())
    news_edit = NewsEdit(img_path=web_path)
    news_crud.edit_news(news_edit, news_id, db)
    if old_web_path != '':
        delete_image_by_web_path(old_web_path)
    return Response(status_code=202)


@router.get('', response_model=List[News])
def get_news(offset=0, count=20, db: Session = Depends(get_db)):
    return news_crud.get_news(offset, count, db)


@router.get('/by_id', response_model=News)
def get_one_news(news_id: int, db: Session = Depends(get_db)):
    return news_crud.get_news_by_id(news_id, db)


@router.get('/count', response_model=int)
def get_news_count(db: Session = Depends(get_db)):
    return news_crud.get_news_count(db)


@router.delete('')
def remove_news(news_id: int, db: Session = Depends(get_db)):
    news = news_crud.get_news_by_id(news_id, db)
    news_crud.remove_news(news_id, db)
    delete_image_by_web_path(news.img_path)
    return Response(status_code=204)
