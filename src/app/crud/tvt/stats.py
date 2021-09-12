from operator import and_
from typing import List

from sqlalchemy.orm import Session

from src.app.exceptions.base import ItemNotFound
from src.app.models.tvt.match import TvtMatch
from src.app.models.tvt.team_stats import TvtStats


def load_not_verified_stats(tournament_id: int, db: Session) -> List[TvtMatch]:
    stats = db.query(TvtStats).filter(and_(TvtStats.confirmed == True, TvtStats.tournament_id == tournament_id)) \
        .order_by(TvtStats.match_id).all()
    if stats is None:
        return []
    return stats


def edit_stats(stats_id: int, score: int, confirmed: bool, proof_path: str, db: Session):
    db.query(TvtStats).filter(TvtStats.id == stats_id).update({
        TvtStats.score: score,
        TvtStats.confirmed: confirmed,
        TvtStats.proof_path: proof_path
    })
    db.commit()


def get_stats(stats_id: int, db: Session) -> TvtStats:
    stats = db.query(TvtStats).filter(TvtStats.id == stats_id).first()
    if stats is None:
        raise ItemNotFound(TvtStats)
    return stats
