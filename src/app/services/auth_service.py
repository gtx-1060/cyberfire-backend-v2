from datetime import timedelta, datetime
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.app.crud.royale.stages import remove_user_from_stages_leaders
from src.app.crud.royale.stats import create_empty_global_stats
from src.app.crud.royale.tournaments import remove_user_from_tournaments_royale
from ..crud.user import *
from ..schemas.user import User, UserCreate
from ..models.roles import Roles
from ..models.user import User as DbUser
from ..config import REFRESH_TOKEN_EXPIRE_DAYS
from ..exceptions.auth_exceptions import AuthenticationException, WrongCredentialsException, NotEnoughPermissions, \
    UserWasBannedException
from ..schemas.token_data import TokenData, Tokens
from ..middleware.auth_middleware import MyOAuth2PasswordBearer
from ..utils import verify_hashed, delete_image_by_web_path, generate_jwt, data_from_jwt

oauth2_scheme = MyOAuth2PasswordBearer(tokenUrl='/api/v2/users/login')


def get_scope(user: User) -> str:
    return user.role.value


def get_role(scope: str) -> Roles:
    try:
        role = Roles(scope)
    except Exception as e:
        print(e)
        raise AuthenticationException("wrong role in access token")
    return role


def create_jwt_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    if not expires_delta:
        expires_delta = timedelta(minutes=30)
    payload = {'mail': user.email, 'scope': get_scope(user)}
    encoded_jwt = generate_jwt(payload, expires_delta)
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    payload = data_from_jwt(token)
    if payload is None:
        raise AuthenticationException('access token is wrong or expired')
    email: str = payload.get("mail")
    role = get_role(payload.get("scope"))
    if email is None:
        raise AuthenticationException('wrong access token')
    return TokenData(email, role)


def try_auth_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[TokenData]:
    if token is None:
        return None
    return decode_token(token)


def auth_user(token: Optional[str] = Depends(oauth2_scheme)) -> TokenData:
    if token is None:
        raise AuthenticationException('token header is empty')
    return decode_token(token)


def auth_admin(data: TokenData = Depends(auth_user)) -> TokenData:
    if data.role != Roles.ADMIN:
        raise NotEnoughPermissions()
    return data


def __auth_with_password(password: str, email: str, db: Session) -> DbUser:
    current_user = get_user_by_email(email, db)
    if not current_user:
        raise WrongCredentialsException()
    if not verify_hashed(current_user.hashed_password, password):
        raise WrongCredentialsException()
    return current_user


def log_in(security_form: OAuth2PasswordRequestForm, db: Session) -> Tokens:
    user = __auth_with_password(security_form.password, security_form.username, db)
    if not user.is_active:
        raise AuthenticationException('user was banned')
    print(user.email)
    access_token = create_jwt_token(user)
    refresh_token = create_jwt_token(user, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    update_refresh_token(user.email, refresh_token, db)
    print(refresh_token)
    return Tokens(access_token=access_token, refresh_token=refresh_token, token_type="Bearer")


def register(user: UserCreate, db: Session):
    create_user(user, db)
    create_empty_global_stats(user.email, db)


def change_user_password(old_password: str, new_password: str, email: str, db: Session):
    user = get_user_by_email(email, db)
    if not verify_hashed(user.hashed_password, old_password):
        raise WrongCredentialsException()
    phash = utils.get_str_hash(new_password)
    update_user_password(email, phash, db)


def authorize_using_refresh(refresh_token: str, db: Session) -> Tokens:
    data = decode_token(refresh_token)
    user = get_user_by_email(data.email, db)
    if refresh_token != user.refresh_token:
        raise AuthenticationException('wrong refresh token')
    if not user.is_active:
        raise UserWasBannedException(user.username)
    access_token = create_jwt_token(user)
    new_refresh_token = create_jwt_token(user, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    update_refresh_token(user.email, new_refresh_token, db)
    print(new_refresh_token)
    return Tokens(access_token=access_token, refresh_token=new_refresh_token, token_type="Bearer")


def ban_user(user_team: str, db: Session):
    user = get_user_by_team(user_team, db)
    user.is_active = False
    remove_user_from_tournaments_royale(user.id, db)


def remove_user_completely(user_team: str, db: Session):
    user = get_user_by_team(user_team, db)
    remove_user_from_tournaments_royale(user.id, db)
    remove_user_from_stages_leaders(user.id, db)
    delete_image_by_web_path(user.avatar_path)
    remove_user(user.id, db)
