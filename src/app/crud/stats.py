from sqlalchemy.orm import Session
from typing import List

from .user import user_by_team
from ..models.games import Games
from ..schemas import stats as stats_schemas
from ..models.stats import MatchStats, TournamentStats, GlobalStats
from ..exceptions.base import ItemNotFound


def get_match_stats(stage_id: int, db: Session) -> List[MatchStats]:
    matches = db.query(MatchStats).filter(MatchStats.stage_id == stage_id).order_by(MatchStats.score.desc()).all()
    if matches is None:
        return []
    return matches


def create_match_stats(stats: stats_schemas.MatchStatsCreate, stage_id: int, db: Session):
    user = user_by_team(stats.team_name, db)
    db_stats = MatchStats(
        game=stats.game,
        kills_count=stats.kills_count,
        score=stats.score,
        user_id=user.id,
        map=stats.map,
        stage_id=stage_id,
        index=stats.index,
        rival_id=stats.rival_id
    )
    db.add(db_stats)
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
    db.add(db_stats)
    db.commit()


def get_tournament_stats(tournament_id: int, db: Session) -> List[TournamentStats]:
    stats = db.query(TournamentStats).filter(TournamentStats.tournament_id == tournament_id)\
        .order_by(TournamentStats.score.desc()).all()
    if stats is None:
        return []
    return stats


def create_tournament_stats(stats: stats_schemas.TournamentStatsCreate, tournament_id: int, db: Session):
    user = user_by_team(stats.team_name, db)
    db_stats = TournamentStats(
        game=stats.game,
        kills_count=stats.kills_count,
        score=stats.score,
        user_id=user.id,
        tournament_id=tournament_id
    )
    db.add(db_stats)
    db.commit()


def edit_tournament_stats(stats: stats_schemas.TournamentStatsEdit, stats_id: int, db: Session):
    db_stats = db.query(TournamentStats).filter(TournamentStats.id == stats_id).first()
    if db_stats is None:
        raise ItemNotFound()
    if stats.score is not None:
        db_stats.score = stats.score
    if stats.kills_count is not None:
        db_stats.kills_count = stats.kills_count
    db.add(db_stats)
    db.commit()


def get_global_stats(game: Games, offset: int, count: int, db: Session) -> List[GlobalStats]:
    stats = db.query(GlobalStats).filter(GlobalStats.game == game).order_by(GlobalStats.score.desc()) \
        .offset(offset).limit(count).all()
    if stats is None:
        return []
    return stats


def create_global_stats(stats: stats_schemas.GlobalStatsCreate, db: Session):
    user = user_by_team(stats.team_name, db)
    db_stats = TournamentStats(
        game=stats.game,
        kills_count=stats.kills_count,
        score=stats.score,
        user_id=user.id,
        wins_count=stats.wins_count
    )
    db.add(db_stats)
    db.commit()


def edit_global_stats(stats: stats_schemas.GlobalStatsEdit, user_id: int, db: Session):
    db_stats = db.query(GlobalStats).filter(GlobalStats.user_id == user_id).first()
    if db_stats is None:
        raise ItemNotFound()
    if stats.score is not None:
        db_stats.score = stats.score
    if stats.kills_count is not None:
        db_stats.kills_count = stats.kills_count
    if stats.wins_count is not None:
        db_stats.wins_count = stats.wins_count
    db.add(db_stats)
    db.commit()
