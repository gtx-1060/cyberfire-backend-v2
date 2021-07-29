from typing import List

from fastapi import APIRouter
from fastapi.params import File, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.responses import Response

from src.app.crud import stats as stats_crud
from src.app.models.games import Games
from src.app.schemas.stats import MatchStats, TournamentStats, GlobalStats, MatchStatsCreate
from src.app.services.auth import auth_admin
from src.app.utils import get_db

router = APIRouter(
    prefix="/api/v2/stats",
    tags=["stats"],
    responses={404: {"description": "Not found"}},
)


@router.get('/matches', response_model=List[MatchStats])
def get_math_stats(stage_id: int, db: Session = Depends(get_db)):
    return stats_crud.get_match_stats(stage_id, db)


@router.get('/tournament', response_model=List[TournamentStats])
def get_tournament_stats(tournament_id: int, db: Session = Depends(get_db)):
    return stats_crud.get_tournament_stats(tournament_id, db)


@router.get('/', response_model=List[GlobalStats])
def get_global_stats(game: Games, offset=0, count=20, db: Session = Depends(get_db)):
    db_stats = stats_crud.get_global_stats(game, offset, count, db)
    stats: GlobalStats = db_stats[0]
    return [stats]


@router.post('/match')
def create_match_stats(stats_list: List[MatchStatsCreate], stage_id: int, db: Session = Depends(get_db),
                       auth_data=Depends(auth_admin)):
    for stats in stats_list:
        stats_crud.create_match_stats(stats, stage_id, db, False)
    db.commit()
    return Response(status_code=202)
