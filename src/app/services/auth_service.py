from datetime import timedelta, datetime
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..crud.stats import create_empty_global_stats
from ..crud.user import *
from ..schemas.user import User, UserCreate
from ..models.roles import Roles
from ..models.user import User as DbUser
from ..config import SECRET_KEY, ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS
from ..exceptions.auth_exceptions import AuthenticationException, WrongCredentialsException, NotEnoughPermissions
from ..schemas.token_data import TokenData, Tokens
from ..middleware.auth_middleware import MyOAuth2PasswordBearer
from ..utils import verify_password

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
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)

    to_encode = {'mail': user.email, 'exp': expire, 'scope': get_scope(user)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("mail")
        role = get_role(payload.get("scope"))
        if email is None:
            raise AuthenticationException('wrong access token')
        return TokenData(email, role)
    except JWTError:
        raise AuthenticationException('access token is wrong or expired')


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
    if not verify_password(current_user.hashed_password, password):
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
    return Tokens(access_token=access_token, refresh_token=refresh_token, token_type="Bearer")


def register(user: UserCreate, db: Session):
    create_user(user, db)
    create_empty_global_stats(user.email, db)


def change_user_password(old_password: str, new_password: str, email: str, db: Session):
    user = get_user_by_email(email, db)
    if not verify_password(user.hashed_password, old_password):
        WrongCredentialsException()
    update_user_password(email, new_password, db)


def authorize_using_refresh(refresh_token: str, db: Session) -> Tokens:
    data = decode_token(refresh_token)
    user = get_user_by_email(data.email, db)
    if refresh_token != user.refresh_token:
        raise AuthenticationException('wrong refresh token')
    if not user.is_active:
        raise AuthenticationException('user was banned')
    access_token = create_jwt_token(user)
    new_refresh_token = create_jwt_token(user, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    update_refresh_token(user.email, new_refresh_token, db)
    return Tokens(access_token=access_token, refresh_token=new_refresh_token, token_type="Bearer")


def ban_user(user_team: str, db: Session):
    user = get_user_by_team(user_team, db)
    user.is_active = False
    db.add(user)
    db.commit()
