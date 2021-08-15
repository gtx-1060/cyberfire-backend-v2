from sqlalchemy import and_
from sqlalchemy.orm import Session
from typing import List, Optional

from .stages import get_stage_by_id
from .user import get_user_by_team
from ..models.stats import MatchStats
from ..schemas import lobbies as lobbies_schemas
from ..models.lobbies import Lobby
from ..exceptions.base import ItemNotFound
from ..schemas.lobbies import LobbyCreate


def get_lobby(lobby_id: int, db: Session) -> Lobby:
    lobby = db.query(Lobby).filter(Lobby.id == lobby_id).first()
    if lobby is None:
        raise ItemNotFound()
    return lobby


def get_lobbies(stage_id: int, db: Session) -> List[Lobby]:
    lobbies = db.query(Lobby).filter(Lobby.stage_id == stage_id).order_by(Lobby.id).all()
    if lobbies is None:
        return []
    return lobbies


def create_lobby(lobby_create: lobbies_schemas.LobbyCreate, db: Session, commit=True) -> Optional[Lobby]:
    get_stage_by_id(lobby_create.stage_id, db)
    db_lobby = Lobby(
        matches_count=lobby_create.matches_count,
        stage_id=lobby_create.stage_id
    )
    db.add(db_lobby)
    if commit:
        db.commit()
        db.refresh(db_lobby)
        return db_lobby


def create_lobbies(lobbies: List[LobbyCreate], db: Session):
    for lobby in lobbies:
        create_lobby(lobby, db, False)
    db.commit()


def edit_lobby(lobby_edit: lobbies_schemas.LobbyEdit, lobby_id: int, db: Session):
    db_lobby = get_lobby(lobby_id, db)
    if lobby_edit.matches_count is not None:
        db_lobby.matches_count = lobby_edit.matches_count
    if lobby_edit.key is not None:
        db_lobby.key = lobby_edit.key
    db.add(db_lobby)
    db.commit()


def remove_lobby(lobby_id: int, db: Session):
    get_lobby(lobby_id, db)
    db.query(Lobby).filter(Lobby.id == lobby_id).delete()
    db.commit()


def remove_team(lobby_id: int, team_name: str, db: Session):
    user = get_user_by_team(team_name, db)
    db.query(MatchStats).filter(and_(MatchStats.lobby_id == lobby_id, MatchStats.user_id == user.id)).delete()
    db.commit()
