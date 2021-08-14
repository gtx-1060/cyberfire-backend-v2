from fastapi import APIRouter, Depends, UploadFile
from fastapi.params import File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.responses import Response

from src.app.config import AVATARS_STATIC_PATH
from src.app.crud.user import get_user_by_email, edit_user, update_user_role, remove_user
from src.app.models.roles import Roles
from src.app.schemas.token_data import Tokens, TokenData
from src.app.schemas.user import UserCreate, User, UserEdit
from src.app.services import auth_service
from src.app.services.auth_service import auth_admin, auth_user, try_auth_user
from src.app.utils import get_db, save_image, delete_image_by_web_path

router = APIRouter(
    prefix="/api/v2/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post('/register')
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    auth_service.register(user, db)
    return Response(status_code=202)


@router.post('/login', response_model=Tokens)
def authorize_user(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return auth_service.log_in(form, db)


@router.get("/me", response_model=User)
async def get_user_status(data: TokenData = Depends(auth_user), db: Session = Depends(get_db)):
    return get_user_by_email(data.email, db)


@router.put("")
def update_user(user_edit: UserEdit, data: TokenData = Depends(auth_user), db: Session = Depends(get_db)):
    edit_user(user_edit, data.email, db)
    return Response(status_code=200)


@router.get("/refresh", response_model=Tokens)
def refresh_tokens(refresh_token: str, db: Session = Depends(get_db)):
    return auth_service.authorize_using_refresh(refresh_token, db)


@router.get("/change_password")
def change_password(old_password: str, new_password: str, user_data=Depends(auth_user), db: Session = Depends(get_db)):
    auth_service.change_user_password(old_password, new_password, user_data.email, db)
    return Response(status_code=200)


@router.post("/upload_avatar")
def upload_avatar(image: UploadFile = File(...), data=Depends(auth_user), db: Session = Depends(get_db)):
    old_web_path = get_user_by_email(data.email, db).avatar_path
    web_path = save_image(AVATARS_STATIC_PATH, image.file.read())
    user_edit = UserEdit(avatar_path=web_path)
    edit_user(user_edit, data.email, db)
    if old_web_path != '':
        delete_image_by_web_path(old_web_path)
    return Response(status_code=202)


@router.get("/ban")
def ban_user(team_name: str, _=Depends(auth_admin), db: Session = Depends(get_db)):
    auth_service.ban_user(team_name, db)
    return Response(status_code=200)


@router.delete("")
def delete_user(team_name: str, _=Depends(auth_admin), db: Session = Depends(get_db)):
    remove_user(team_name, db)
    return Response(status_code=200)


@router.get("/be_admin")
def give_admin_rights(secret_key: str, user_data=Depends(auth_user), db: Session = Depends(get_db)):
    """WARNING: ONLY FOR TESTS!!!"""
    if secret_key != "mavrin":
        return Response(content="chill the fuck out man", status_code=411)
    update_user_role(user_data.email, Roles.ADMIN, db)
    return Response(status_code=200)




