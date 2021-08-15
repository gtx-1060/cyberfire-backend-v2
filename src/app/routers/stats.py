from typing import List, Dict
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette.responses import Response

from src.app.crud import stats as stats_crud
from src.app.crud.lobbies import get_lobbies, get_lobby
from src.app.crud.stages import get_stage_by_id
from src.app.crud.user import get_user_by_email
from src.app.models.games import Games
from src.app.models.tournament_states import StageStates
from src.app.schemas.stats import MatchStats, TournamentStats, GlobalStats, MatchStatsCreate, MatchStatsEdit
from src.app.schemas.token_data import TokenData
from src.app.services.auth_service import auth_admin, try_auth_user
from src.app.services.lobby_service import convert_lobbies_to_frontend_ready, convert_lobby_to_frontend_ready
from src.app.services.tournaments_service import save_row_stats
from src.app.utils import get_db

router = APIRouter(
    prefix="/api/v2/stats",
    tags=["stats"],
    responses={404: {"description": "Not found"}},
)


@router.get('/stage', response_model=dict)
def get_math_stats(stage_id: int, user_data: TokenData = Depends(try_auth_user), db: Session = Depends(get_db)):
    stage = get_stage_by_id(stage_id, db)
    user = get_user_by_email(user_data.email, db)
    data, lobby_key = convert_lobbies_to_frontend_ready(stage.lobbies, user.team_name)
    return {'lobbies': data, "key": lobby_key}


@router.get('/lobby', response_model=dict)
def get_math_stats(lobby_id: int, user_data: TokenData = Depends(try_auth_user), db: Session = Depends(get_db)):
    lobby = get_lobby(lobby_id, db)
    user = get_user_by_email(user_data.email, db)
    data, key = convert_lobby_to_frontend_ready(lobby, user.team_name)
    if data is None:
        return {'lobby': [], "key": ''}
    return {'lobby': data, "key": key}


@router.get('/tournament', response_model=List[TournamentStats])
def get_tournament_stats(tournament_id: int, db: Session = Depends(get_db)):
    return stats_crud.get_tournament_stats(tournament_id, db)


@router.get('', response_model=List[GlobalStats])
def get_global_stats(game: Games, offset=0, count=20, db: Session = Depends(get_db)):
    db_stats = stats_crud.get_global_stats(game, offset, count, db)
    return db_stats


@router.post('/matches')
def create_new_multiple_match_stats(stats_list: List[MatchStatsCreate], lobby_id: int,
                                    db: Session = Depends(get_db), _=Depends(auth_admin)):
    save_row_stats(stats_list, lobby_id, db)
    return Response(status_code=202)


@router.post('/match')
def create_match_stats(stats: MatchStatsCreate, lobby_id: int, db: Session = Depends(get_db),
                       _=Depends(auth_admin)):
    get_lobby(lobby_id, db)
    stats_crud.create_match_stats(stats, lobby_id, db)
    return Response(status_code=202)


@router.put('/match')
def edit_match_stats(match: MatchStatsEdit, match_id: int, db: Session = Depends(get_db),
                     _=Depends(auth_admin)):
    stats_crud.edit_match_stats(match, match_id, db)
    return Response(status_code=200)
