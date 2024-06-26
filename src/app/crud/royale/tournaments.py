from sqlalchemy import exists, and_
from sqlalchemy.orm import Session
from typing import List, Optional

from src.app.config import DEFAULT_IMAGE_PATH
from src.app.exceptions.db_exceptions import FieldCouldntBeEdited
from src.app.models.games import Games
from src.app.models.royale.tournament import Tournament, association_table as tournament_associations
from src.app.exceptions.base import ItemNotFound
from src.app.models.tournament_states import TournamentStates
from src.app.models.user import User
from src.app.schemas.royale.tournaments import TournamentCreate, TournamentEdit


def is_tournament_exists_royale(tournament_id: int, db: Session) -> bool:
    return db.query(exists().where(Tournament.id == tournament_id)).scalar()


def get_tournaments_royale(game: Optional[Games], offset: int, limit: int, db: Session) -> List[Tournament]:
    tournaments = None
    if game is None:
        tournaments = db.query(Tournament).order_by(Tournament.start_date.desc()).offset(offset).limit(limit).all()
    else:
        tournaments = db.query(Tournament).filter(Tournament.game == game).order_by(Tournament.start_date.desc())\
            .offset(offset).limit(limit).all()
    if tournaments is None:
        return []
    return tournaments


def get_tournament_royale(tournament_id: int, db: Session) -> Tournament:
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if tournament is None:
        raise ItemNotFound(Tournament)
    return tournament


def get_tournaments_count_royale(db: Session, game: Games) -> int:
    return db.query(Tournament).filter(Tournament.game == game).count()


def create_tournament_royale(tournament: TournamentCreate, db: Session) -> Tournament:
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


def edit_tournament_royale(tournament: TournamentEdit, tournament_id: int, db: Session):
    db_tournament = get_tournament_royale(tournament_id, db)
    if tournament.title is not None:
        db_tournament.title = tournament.title
    if tournament.description is not None:
        db_tournament.description = tournament.description
    if tournament.rewards is not None:
        db_tournament.rewards = tournament.rewards
    if tournament.stream_url is not None:
        db_tournament.stream_url = tournament.stream_url
    if tournament.img_path is not None:
        db_tournament.img_path = tournament.img_path
    if tournament.max_squads is not None:
        if count_users_in_tournament_royale(tournament_id, db) > tournament.max_squads:
            raise FieldCouldntBeEdited("max_squads", "the tournament have more registered users")
        db_tournament.max_squads = tournament.max_squads
    db.add(db_tournament)
    db.commit()


def remove_user_from_tournaments_royale(user_id: int, db: Session):
    db.query(tournament_associations).filter(tournament_associations.c.users_id == user_id).delete()
    db.commit()


def remove_user_from_tournament_royale(user_id: int, tournament_id: int, db: Session):
    db.query(tournament_associations).filter(and_(tournament_associations.c.users_id == user_id,
                                                  tournament_associations.c.tournaments_id == tournament_id)).delete()
    db.commit()


def remove_tournament_royale(tournament_id: int, db: Session):
    db.query(tournament_associations).filter(tournament_associations.c.tournaments_id == tournament_id).delete()
    db.query(Tournament).filter(Tournament.id == tournament_id).delete()
    db.commit()


def count_users_in_tournament_royale(tournament_id: int, db: Session):
    return db.query(User).join(Tournament, User.tournaments).filter(Tournament.id == tournament_id).count()


def is_user_in_tournament_royale(tournament_id: int, user_email: str, db: Session) -> bool:
    return (db.query(Tournament).join(User, Tournament.users)
            .filter(and_(Tournament.id == tournament_id, User.email == user_email)).first()) is not None


def update_tournament_state_royale(new_state: TournamentStates, tournament_id: int, db: Session):
    db.query(Tournament).filter(Tournament.id == tournament_id).update({
        Tournament.state: new_state
    })
    db.commit()

