from fastapi import APIRouter, Depends, UploadFile
from fastapi.params import File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.responses import Response

from src.app.config import AVATARS_STATIC_PATH
from src.app.crud.user import get_user_by_email, edit_user
from src.app.schemas.token_data import Tokens, TokenData
from src.app.schemas.user import UserCreate, User, UserEdit
from src.app.services.auth import auth_user, register, log_in, authorize_using_refresh
from src.app.utils import get_db, save_image, delete_image_by_web_path

router = APIRouter(
    prefix="/api/v2/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post('/register')
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    register(user, db)
    return Response(status_code=202)


@router.post('/login', response_model=Tokens)
def authorize_user(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return log_in(form, db)


@router.get("/me", response_model=User)
def get_user_status(data: TokenData = Depends(auth_user), db: Session = Depends(get_db)):
    return get_user_by_email(data.email, db)


@router.put("/")
def update_user(user_edit: UserEdit, data: TokenData = Depends(auth_user), db: Session = Depends(get_db)):
    edit_user(user_edit, data.email, db)
    return Response(status_code=202)


@router.get("/refresh", response_model=Tokens)
def refresh_tokens(refresh_token: str, db: Session = Depends(get_db)):
    return authorize_using_refresh(refresh_token, db)


@router.post("/upload_avatar")
def upload_avatar(image: UploadFile = File(...), data=Depends(auth_user), db: Session = Depends(get_db)):
    old_web_path = get_user_by_email(data.email, db).avatar_path
    web_path = save_image(AVATARS_STATIC_PATH, image.file.read())
    user_edit = UserEdit(avatar_path=web_path)
    edit_user(user_edit, data.email, db)
    if old_web_path != '':
        delete_image_by_web_path(old_web_path)
    return Response(status_code=202)












