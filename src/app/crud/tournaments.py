from sqlalchemy import exists, and_
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from .user import get_user_by_email
from ..config import DEFAULT_IMAGE_PATH
from ..exceptions.db_exceptions import FieldCouldntBeEdited
from ..exceptions.tournament_exceptions import MaxSquadsCount, UserAlreadyRegistered, UserNotRegistered, \
    WrongTournamentState
from ..models.games import Games
from ..models.tournament import Tournament
from ..exceptions.base import ItemNotFound
from ..models.tournament_states import TournamentStates
from ..models.user import User
from ..schemas.tournaments import TournamentCreate, TournamentEdit


def is_tournament_exists(tournament_id: int, db: Session) -> bool:
    return db.query(exists().where(Tournament.id == tournament_id)).scalar()


def get_tournaments(game: Optional[Games], offset: int, limit: int, db: Session) -> List[Tournament]:
    tournaments = None
    if game is None:
        tournaments = db.query(Tournament).order_by(Tournament.start_date.desc()).offset(offset).limit(limit).all()
    else:
        tournaments = db.query(Tournament).filter(Tournament.game == game).order_by(Tournament.start_date.desc())\
            .offset(offset).limit(limit).all()
    if tournaments is None:
        return []
    return tournaments


def get_tournament(tournament_id: int, db: Session) -> Tournament:
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if tournament is None:
        raise ItemNotFound()
    return tournament


def get_tournaments_count(db: Session) -> int:
    return db.query(Tournament).count()


def create_tournament(tournament: TournamentCreate, db: Session) -> Tournament:
    db_tournament = Tournament(
        title=tournament.title,
        description=tournament.description,
        state=TournamentStates.REGISTRATION,
        rewards=tournament.rewards,
        stream_url=tournament.stream_url,
        stages_count=len(tournament.stages),
        game=tournament.game,
        img_path=DEFAULT_IMAGE_PATH,
        max_squads=tournament.max_squads,
        start_date=tournament.start_date,
        end_date=tournament.end_date
    )

    db.add(db_tournament)
    db.commit()
    db.refresh(db_tournament)
    return db_tournament


def edit_tournament(tournament: TournamentEdit, tournament_id: int, db: Session):
    db_tournament = get_tournament(tournament_id, db)
    if tournament.title is not None:
        db_tournament.title = tournament.title
    if tournament.description is not None:
        db_tournament.description = tournament.description
    if tournament.rewards is not None:
        db_tournament.rewards = tournament.rewards
    if tournament.stream_url is not None:
        db_tournament.stream_url = tournament.stream_url
    if tournament.max_squads is not None:
        if count_users_in_tournament(tournament_id, db) > tournament.max_squads:
            raise FieldCouldntBeEdited("max_squads", "the tournament have more registered users")
        if db_tournament.state == TournamentStates.IS_ON:
            raise FieldCouldntBeEdited("max_squads", "the tournament is on")
        db_tournament.max_squads = tournament.max_squads
    db.add(db_tournament)
    db.commit()


def remove_tournament(tournament_id: int, db: Session):
    db.query(Tournament).filter(Tournament.id == tournament_id).delete()
    db.commit()


def count_users_in_tournament(tournament_id: int, db: Session):
    return db.query(User).join(Tournament, User.tournaments).filter(Tournament.id == tournament_id).count()


def is_users_in_tournament(tournament_id: int, user_email: str, db: Session) -> bool:
    return (db.query(Tournament).join(User, Tournament.users)
            .filter(and_(Tournament.id == tournament_id, User.email == user_email)).first()) is not None


def update_tournament_state(new_state: TournamentStates, tournament_id: int, db: Session):
    db.query(Tournament).filter(Tournament.id == tournament_id).update({
        Tournament.state: new_state
    })
    db.commit()


def add_user_to_tournament(tournament_id: int, user_email: str, db: Session):
    user = get_user_by_email(user_email, db)
    tournament = get_tournament(tournament_id, db)
    if tournament.state != TournamentStates.REGISTRATION:
        raise WrongTournamentState()
    if user in tournament.users:
        raise UserAlreadyRegistered(user_email)
    if len(tournament.users) < tournament.max_squads:
        tournament.users.append(user)
    else:
        raise MaxSquadsCount()
    db.add(tournament)
    db.commit()


def remove_tournament_player(tournament_id: int, user_email: str, db: Session):
    user = get_user_by_email(user_email, db)
    tournament = get_tournament(tournament_id, db)
    if tournament.state != TournamentStates.REGISTRATION:
        raise WrongTournamentState()
    if user in tournament.users:
        tournament.users.remove(user)
    else:
        raise UserNotRegistered(user_email)
    db.add(tournament)
    db.commit()