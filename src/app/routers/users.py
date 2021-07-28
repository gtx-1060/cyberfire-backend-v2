from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.responses import Response

from src.app.crud.user import get_user_by_email, edit_user
from src.app.schemas.token_data import Tokens, TokenData
from src.app.schemas.user import UserCreate, User, UserEdit
from src.app.services import auth
from src.app.services.auth import auth_user
from src.app.utils import get_db

router = APIRouter(
    prefix="api/v2/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post('/register')
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    auth.register(user, db)
    return Response(status_code=202)


@router.post('/login', response_model=Tokens)
def authorize_user(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return auth.log_in(form, db)


@router.get("/me", response_model=User)
def get_user_status(data: TokenData = Depends(auth_user), db: Session = Depends(get_db)):
    return get_user_by_email(data.email, db)


@router.put("/")
def update_user(user_edit: UserEdit, data: TokenData = Depends(auth_user), db: Session = Depends(get_db)):
    edit_user(user_edit, data.email, db)
    return Response(status_code=202)

