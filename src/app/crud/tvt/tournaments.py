from sqlalchemy import exists, and_
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple

from src.app.config import DEFAULT_IMAGE_PATH
from src.app.exceptions.db_exceptions import FieldCouldntBeEdited
from src.app.models.games import Games
from src.app.models.tvt.match import TvtMatch
from src.app.models.tvt.stage import TvtStage
from src.app.models.tvt.team_stats import TvtStats
from src.app.models.tvt.tournament import TvtTournament as Tournament, association_table as tournament_associations
from src.app.exceptions.base import ItemNotFound
from src.app.models.tournament_states import TournamentStates, StageStates
from src.app.models.user import User
from src.app.schemas.tvt.tournaments import TvtTournamentCreate, TvtTournamentEdit


def is_tournament_exists_tvt(tournament_id: int, db: Session) -> bool:
    return db.query(exists().where(Tournament.id == tournament_id)).scalar()


def get_tournaments_tvt(game: Optional[Games], offset: int, limit: int, db: Session) -> List[Tournament]:
    tournaments = None
    if game is None:
        tournaments = db.query(Tournament).order_by(Tournament.start_date.desc()).offset(offset).limit(limit).all()
    else:
        tournaments = db.query(Tournament).filter(Tournament.game == game).order_by(Tournament.start_date.desc())\
            .offset(offset).limit(limit).all()
    if tournaments is None:
        return []
    return tournaments


def get_tournament_tvt(tournament_id: int, db: Session) -> Tournament:
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if tournament is None:
        raise ItemNotFound(Tournament)
    return tournament


def get_tournaments_count_tvt(db: Session) -> int:
    return db.query(Tournament).count()


def create_tournament_tvt(tournament: TvtTournamentCreate, db: Session) -> Tournament:
    db_tournament = Tournament(
        title=tournament.title,
        description=tournament.description,
        state=TournamentStates.REGISTRATION,
        rewards=tournament.rewards,
        stream_url=tournament.stream_url,
        game=tournament.game,
        img_path=DEFAULT_IMAGE_PATH,
        max_squads=tournament.max_squads,
        start_date=tournament.start_date
    )

    db.add(db_tournament)
    db.commit()
    db.refresh(db_tournament)
    return db_tournament


def edit_tournament_tvt(tournament: TvtTournamentEdit, tournament_id: int, db: Session):
    db_tournament = get_tournament_tvt(tournament_id, db)
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
    if tournament.start_date is not None:
        db_tournament.start_date = tournament.start_date
    if tournament.max_squads is not None:
        if count_users_in_tournament_tvt(tournament_id, db) > tournament.max_squads:
            raise FieldCouldntBeEdited("max_squads", "the tournament have more registered users")
        db_tournament.max_squads = tournament.max_squads
    db.add(db_tournament)
    db.commit()


def remove_user_from_tournaments_tvt(user_id: int, db: Session):
    db.query(tournament_associations).filter(tournament_associations.c.users_id == user_id).delete()
    db.commit()


def remove_user_from_tournament_tvt(user_id: int, tournament_id: int, db: Session):
    db.query(tournament_associations).filter(and_(tournament_associations.c.users_id == user_id,
                                                  tournament_associations.c.tournaments_id == tournament_id)).delete()
    db.commit()


def remove_tournament_tvt(tournament_id: int, db: Session):
    db.query(tournament_associations).filter(tournament_associations.c.tournaments_id == tournament_id).delete()
    db.query(Tournament).filter(Tournament.id == tournament_id).delete()
    db.commit()


def count_users_in_tournament_tvt(tournament_id: int, db: Session):
    return db.query(User).join(Tournament, User.tournaments).filter(Tournament.id == tournament_id).count()


def is_user_in_tournament_tvt(tournament_id: int, user_email: str, db: Session) -> bool:
    return (db.query(Tournament).join(User, Tournament.users)
            .filter(and_(Tournament.id == tournament_id, User.email == user_email)).first()) is not None


def update_tournament_state_tvt(new_state: TournamentStates, tournament_id: int, db: Session):
    db.query(Tournament).filter(Tournament.id == tournament_id).update({
        Tournament.state: new_state
    })
    db.commit()


def get_last_tournament_stage(tournament_id: int, db: Session):
    last_stage: TvtStage = db.query(TvtStage).filter(Tournament.id == tournament_id).order_by(
        TvtStage.id.desc()).first()
    return last_stage


def user_last_stage_match(user_id: int, last_stage: TvtStage, db: Session) -> Optional[TvtMatch]:
    match = db.query(TvtMatch).join(TvtStats, TvtMatch.teams_stats).filter(and_(TvtMatch.stage_id == last_stage.id,
                                                                                TvtStats.user_id == user_id)).first()
    return match