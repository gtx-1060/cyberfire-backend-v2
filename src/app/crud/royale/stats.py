from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import and_

from src.app.crud.user import user_by_team, get_user_by_email
from src.app.exceptions.db_exceptions import SameItemAlreadyExists
from src.app.models.games import Games
from src.app.models.user import User
from src.app.schemas.royale import stats as stats_schemas
from src.app.models.royale.stats import MatchStats, TournamentStats, GlobalStats
from src.app.exceptions.base import ItemNotFound


def get_match_stats(lobby_id: int, db: Session) -> List[MatchStats]:
    matches = db.query(MatchStats).filter(MatchStats.stage_id == lobby_id).order_by(MatchStats.score.desc()).all()
    if matches is None:
        return []
    return matches


def get_match_by_team(stage_id: int, team_name: str, db: Session) -> MatchStats:
    stats = db.query(MatchStats).filter(and_(MatchStats.stage_id == stage_id, MatchStats.user.team_name == team_name))\
        .first()
    if stats is None:
        raise ItemNotFound(MatchStats)
    return stats


def create_match_stats(stats: stats_schemas.MatchStatsCreate, lobby_id: int, db: Session, commit=True):
    user = user_by_team(stats.team_name, db)
    db_stats = MatchStats(
        game=stats.game,
        kills_count=stats.kills_count,
        score=stats.score,
        user_id=user.id,
        lobby_id=lobby_id,
        index=stats.index,
        placement=stats.placement
    )
    try:
        db.add(db_stats)
        if commit:
            db.commit()
    except IntegrityError:
        raise SameItemAlreadyExists(f'match stats {user.team_name}')


def create_match_stats_list(stats_list: List[stats_schemas.MatchStatsCreate], lobby_id: int, db: Session):
    for stats in stats_list:
        create_match_stats(stats, lobby_id, db, False)

    try:
        db.commit()
    except IntegrityError:
        raise SameItemAlreadyExists()


def edit_match_stats(stats: stats_schemas.MatchStatsEdit, stats_id: int, db: Session):
    db_stats = db.query(MatchStats).filter(MatchStats.id == stats_id).first()
    if db_stats is None:
        raise ItemNotFound(MatchStats)
    if stats.score is not None:
        db_stats.score = stats.score
    if stats.kills_count is not None:
        db_stats.kills_count = stats.kills_count
    if stats.placement is not None:
        db_stats.placement = stats.placement
    db.add(db_stats)
    db.commit()


def delete_match_stats(stats_id: int, db: Session):
    db.query(MatchStats).filter(MatchStats.id == stats_id).delete()
    db.commit()


def delete_match_by_lobby(team_name: str, lobby_id: int, db: Session):
    match = db.query(MatchStats).join(User)\
        .filter(and_(MatchStats.lobby_id == lobby_id, User.team_name == team_name)).first()
    if match is None:
        raise ItemNotFound(MatchStats)
    db.query(MatchStats).filter(MatchStats.id == match.id).delete()
    db.commit()


def get_tournament_stats(tournament_id: int, db: Session) -> List[TournamentStats]:
    stats = db.query(TournamentStats).filter(TournamentStats.tournament_id == tournament_id)\
        .order_by(TournamentStats.score.desc()).all()
    if stats is None:
        return []
    return stats


def create_tournament_stats(stats: stats_schemas.TournamentStatsCreate, tournament_id: int, db: Session, commit=True):
    user = user_by_team(stats.team_name, db)
    db_stats = TournamentStats(
        game=stats.game,
        kills_count=stats.kills_count,
        score=stats.score,
        user_id=user.id,
        wins_count=stats.wins_count,
        tournament_id=tournament_id
    )
    try:
        db.add(db_stats)
        if commit:
            db.commit()
    except IntegrityError:
        raise SameItemAlreadyExists(f'tournament stats {user.team_name}')


def edit_tournament_stats(stats: stats_schemas.TournamentStatsEdit, stats_id: int, db: Session, commit=True):
    db_stats = db.query(TournamentStats).filter(TournamentStats.id == stats_id).first()
    if db_stats is None:
        raise ItemNotFound(TournamentStats)
    if stats.score is not None:
        db_stats.score = stats.score
    if stats.kills_count is not None:
        db_stats.kills_count = stats.kills_count
    if stats.wins_count is not None:
        db_stats.wins_count = stats.wins_count
    db.add(db_stats)
    if commit:
        db.commit()


def get_global_stats(game: Games, offset: int, count: int, db: Session) -> List[GlobalStats]:
    stats_query = db.query(GlobalStats).filter(GlobalStats.game == game)
    if game == Games.COD_WARZONE or game == Games.APEX or game == Games.FORTNITE:
        stats_query = stats_query.order_by(GlobalStats.score.desc())
    else:
        stats_query = stats_query.order_by(GlobalStats.wins_count.desc())
    stats = stats_query.offset(offset).limit(count).all()
    if stats is None:
        return []
    return stats


def create_empty_global_stats(user_email: str, db: Session):
    user = get_user_by_email(user_email, db)
    for game in Games:
        stats = GlobalStats(
            score=0,
            kills_count=0,
            wins_count=0,
            user_id=user.id,
            game=game
        )
        try:
            db.add(stats)
            db.commit()
        except IntegrityError:
            raise SameItemAlreadyExists(f'global stats {user.team_name}')


def create_global_stats(stats: stats_schemas.GlobalStatsCreate, db: Session):
    user = user_by_team(stats.team_name, db)
    db_stats = GlobalStats(
        game=stats.game,
        kills_count=stats.kills_count,
        score=stats.score,
        user_id=user.id,
        wins_count=stats.wins_count
    )
    try:
        db.add(db_stats)
        db.commit()
    except IntegrityError:
        raise SameItemAlreadyExists(f'global stats {user.team_name}')


def edit_global_stats(added_stats: stats_schemas.GlobalStatsEdit, game: Games, user_id: int, db: Session, commit=True):
    db_stats = db.query(GlobalStats).filter(and_(GlobalStats.user_id == user_id, GlobalStats.game == game)).first()
    if db_stats is None:
        raise ItemNotFound(GlobalStats)
    if added_stats.score is not None:
        db_stats.score += added_stats.score
    if added_stats.kills_count is not None:
        db_stats.kills_count += added_stats.kills_count
    if added_stats.wins_count is not None:
        db_stats.wins_count += added_stats.wins_count
    db.add(db_stats)
    if commit:
        db.commit()
