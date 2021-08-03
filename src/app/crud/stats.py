from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import and_

from .user import user_by_team, get_user_by_email
from ..models.games import Games
from ..models.user import User
from ..schemas import stats as stats_schemas
from ..models.stats import MatchStats, TournamentStats, GlobalStats
from ..exceptions.base import ItemNotFound


def get_match_stats(stage_id: int, db: Session) -> List[MatchStats]:
    matches = db.query(MatchStats).filter(MatchStats.stage_id == stage_id).order_by(MatchStats.score.desc()).all()
    if matches is None:
        return []
    return matches


def get_match_by_team(stage_id: int, team_name: str, db: Session) -> MatchStats:
    stats = db.query(MatchStats).filter(and_(MatchStats.stage_id == stage_id, MatchStats.user.team_name == team_name))\
        .first()
    if stats is None:
        raise ItemNotFound()
    return stats


def create_match_stats(stats: stats_schemas.MatchStatsCreate, stage_id: int, db: Session, commit=True):
    user = user_by_team(stats.team_name, db)
    db_stats = MatchStats(
        game=stats.game,
        kills_count=stats.kills_count,
        score=stats.score,
        user_id=user.id,
        map=stats.map,
        stage_id=stage_id,
        index=stats.index,
        rival_id=stats.rival_id,
        winner=stats.winner
    )
    db.add(db_stats)
    if commit:
        db.commit()


def create_match_stats_list(stats_list: List[stats_schemas.MatchStatsCreate], stage_id: int, db: Session):
    for stats in stats_list:
        create_match_stats(stats, stage_id, db, False)
    db.commit()


def edit_match_stats(stats: stats_schemas.MatchStatsEdit, stats_id: int, db: Session):
    db_stats = db.query(MatchStats).filter(MatchStats.id == stats_id).first()
    if db_stats is None:
        raise ItemNotFound()
    if stats.score is not None:
        db_stats.score = stats.score
    if stats.map is not None:
        db_stats.map = stats.map
    if stats.index is not None:
        db_stats.index = stats.index
    if stats.kills_count is not None:
        db_stats.kills_count = stats.kills_count
    if stats.rival_id is not None:
        db_stats.rival_id = stats.rival_id
    if stats.attended is not None:
        db_stats.attended = stats.attended
    if stats.winner is not None:
        db_stats.winner = stats.winner
    db.add(db_stats)
    db.commit()


# def delete_unassigned_match_stats(stage_id: int, db: Session, commit=True):
#     db.query(MatchStats).filter(and_(MatchStats.stage_id == stage_id, MatchStats.a)).delete()
#     if commit:
#         db.commit()


def delete_match_stats(stats_id: int, db: Session):
    db.query(MatchStats).filter(MatchStats.id == stats_id).delete()
    db.commit()


def delete_match_by_stage(team_name: str, stage_id: int, db: Session):
    match = db.query(MatchStats).join(User)\
        .filter(and_(MatchStats.stage_id == stage_id, User.team_name == team_name)).first()
    if match is None:
        raise ItemNotFound()
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
    db.add(db_stats)
    if commit:
        db.commit()


def edit_tournament_stats(stats: stats_schemas.TournamentStatsEdit, stats_id: int, db: Session, commit=True):
    db_stats = db.query(TournamentStats).filter(TournamentStats.id == stats_id).first()
    if db_stats is None:
        raise ItemNotFound()
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
    stats = db.query(GlobalStats).filter(GlobalStats.game == game).order_by(GlobalStats.score.desc()) \
        .offset(offset).limit(count).all()
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
        db.add(stats)
    db.commit()


def create_global_stats(stats: stats_schemas.GlobalStatsCreate, db: Session):
    user = user_by_team(stats.team_name, db)
    db_stats = GlobalStats(
        game=stats.game,
        kills_count=stats.kills_count,
        score=stats.score,
        user_id=user.id,
        wins_count=stats.wins_count
    )
    db.add(db_stats)
    db.commit()


def edit_global_stats(added_stats: stats_schemas.GlobalStatsEdit, user_id: int, db: Session, commit=True):
    db_stats = db.query(GlobalStats).filter(GlobalStats.user_id == user_id).first()
    if db_stats is None:
        raise ItemNotFound()
    if added_stats.score is not None:
        db_stats.score += added_stats.score
    if added_stats.kills_count is not None:
        db_stats.kills_count += added_stats.kills_count
    if added_stats.wins_count is not None:
        db_stats.wins_count += added_stats.wins_count
    db.add(db_stats)
    if commit:
        db.commit()
