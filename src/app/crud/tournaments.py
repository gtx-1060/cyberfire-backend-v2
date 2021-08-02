from sqlalchemy import exists, and_
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..config import DEFAULT_IMAGE_PATH
from ..exceptions.db_exceptions import FieldCouldntBeEdited
from ..models.games import Games
from ..models.tournament import Tournament
from ..exceptions.base import ItemNotFound
from ..models.tournament_states import States
from ..models.user import User
from ..schemas.tournaments import TournamentCreate, TournamentEdit


def is_tournament_exists(tournament_id: int, db: Session) -> bool:
    return db.query(exists().where(Tournament.id == tournament_id)).scalar()


def get_tournaments(game: Games, db: Session):
    tournaments = None
    if game is None:
        tournaments = db.query(Tournament).order_by(Tournament.start_date.desc()).all()
    else:
        tournaments = db.query(Tournament).filter(Tournament.game == game).order_by(Tournament.start_date.desc()).all()
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
        state=States.REGISTRATION,
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
        if db_tournament.state == States.IS_ON:
            raise FieldCouldntBeEdited("max_squads", "the tournament is on")
        db_tournament.max_squads = tournament.max_squads
    db.add(db_tournament)
    db.commit()


def count_users_in_tournament(tournament_id: int, db: Session):
    return db.query(User).join(Tournament).filter(User.tournament.id == tournament_id).count()


def is_users_in_tournament(tournament_id: int, user_email: str, db: Session):
    return (db.query(Tournament).join(User.email)
            .filter(and_(Tournament.stage_id == tournament_id, User.email == user_email)).first() is not None)


def update_tournament_state(new_state: States, tournament_id: int, db: Session):
    db.query(Tournament).filter(Tournament.id == tournament_id).update({
        Tournament.state: new_state
    })
    db.commit()

# TODO: РЕГИСТРАЦИЯ В ТУРИНРЕ
