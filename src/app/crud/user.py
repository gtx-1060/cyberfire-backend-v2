from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..schemas import user as user_schemas
from ..models.user import User
from ..models.squad import Squad
from ..models.roles import Roles
from ..models.games import Games
from ..exceptions import user_exceptions
from .. import utils


def __check_email_unique(email: str, db: Session):
    if not db.query(User).filter(User.email == email).first() is None:
        raise user_exceptions.UserAlreadyExists()


def __check_team_unique(team_name: str, db: Session):
    if not db.query(User).filter(User.team_name == team_name).first() is None:
        raise user_exceptions.UserAlreadyExists()


def __create_squads(user_id: int, db: Session):
    for game in Games:
        squad = Squad(
            game=game,
            user_id=user_id,
            players=[]
        )
        db.add(squad)
    db.commit()


def user_by_team(team_name: str, db: Session) -> User:
    user = db.query(User).filter(User.team_name == team_name).first()
    if user is None:
        raise user_exceptions.UserNotFound()
    return user


def user_id_by_team(team_name: str, db: Session) -> int:
    user_id = db.query(User.id).filter(User.team_name == team_name).first()
    if not user_id:
        raise user_exceptions.UserNotFound()
    return user_id


def create_user(user: user_schemas.UserCreate, db: Session):
    __check_team_unique(user.team_name, db)
    __check_email_unique(user.email, db)
    hashed_pass = utils.get_password_hash(user.password)
    db_user = User(
        email=user.email,
        team_name=user.team_name,
        username=user.username,
        hashed_password=hashed_pass,
        role=Roles.USER,
        refresh_token=''
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    __create_squads(db_user.id, db)


def get_user_by_email(email: str, db: Session) -> User:
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise user_exceptions.UserNotFound()
    return user


def edit_user(user: user_schemas.UserEdit, email: str, db: Session):
    db_user = get_user_by_email(email, db)
    if user.username is not None:
        db_user.username = user.username
    if user.avatar_path is not None:
        db_user.avatar_path = user.avatar_path
    if user.team_name is not None:
        __check_team_unique(user.team_name, db)
        db_user.team_name = user.team_name
    if user.squads is not None and len(user.squads) > 0:
        for squad in user.squads:
            if squad is None:
                # TODO: LOG SOMETHING
                continue
            db_squad = db.query(Squad).filter(and_(Squad.user_id == db_user.id, Squad.game == squad.game)).first()
            db_squad.players = squad.players.copy()
            db.add(db_squad)
    db.add(db_user)
    db.commit()


def update_user_password(user_email: str, new_password_hash: str, db: Session):
    db.query(User).filter(User.email == user_email).update({
        User.hashed_password: new_password_hash
    })
    db.commit()


def update_refresh_token(email: str, new_token: str, db: Session):
    db_user = get_user_by_email(email, db)
    db_user.refresh_token = new_token
    db.add(db_user)
    db.commit()


def get_user_squad_by_email(user_email: str, game: Games, db: Session) -> Squad:
    return db.query(Squad).join(User).filter(and_(User.email == user_email, Squad.game == game)).first()


def get_user_squad_by_team(team: str, game: Games, db: Session) -> Squad:
    return db.query(Squad).join(User).filter(and_(User.team_name == team, Squad.game == game)).first()


def update_user_role(user_email: str, role: Roles, db: Session):
    db.query(User).filter(User.email == user_email).update({
        User.role: role
    })
    db.commit()
