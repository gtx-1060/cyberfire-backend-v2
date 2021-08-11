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
from src.app.routers.stages import get_stage
from src.app.schemas.stats import MatchStats, TournamentStats, GlobalStats, MatchStatsCreate
from src.app.schemas.token_data import TokenData
from src.app.services.auth import auth_admin, try_auth_user
from src.app.services.lobby_service import convert_lobbies_to_frontend_ready, convert_lobby_to_frontend_ready
from src.app.utils import get_db

router = APIRouter(
    prefix="/api/v2/stats",
    tags=["stats"],
    responses={404: {"description": "Not found"}},
)


@router.get('/stage', response_model=dict)
def get_math_stats(stage_id: int, user_data: TokenData = Depends(try_auth_user), db: Session = Depends(get_db)):
    stage = get_stage_by_id(stage_id, db)
    key_needed = stage.state == StageStates.IS_ON
    if user_data is not None:
        user_team = get_user_by_email(user_data.email, db).team_name
    else:
        user_team = ''
    data, key = convert_lobbies_to_frontend_ready(stage.lobbies, user_team, key_needed, db)
    return {"lobbies": data, "lobby_key": key}


@router.get('/lobby', response_model=dict)
def get_math_stats(lobby_id: int, db: Session = Depends(get_db)):
    lobby = get_lobby(lobby_id, db)
    data = convert_lobby_to_frontend_ready(lobby)
    if data is None:
        return {}
    return data


@router.get('/tournament', response_model=List[TournamentStats])
def get_tournament_stats(tournament_id: int, db: Session = Depends(get_db)):
    return stats_crud.get_tournament_stats(tournament_id, db)


@router.get('', response_model=List[GlobalStats])
def get_global_stats(game: Games, offset=0, count=20, db: Session = Depends(get_db)):
    db_stats = stats_crud.get_global_stats(game, offset, count, db)
    stats: GlobalStats = db_stats[0]
    return [stats]


@router.post('/match')
def create_match_stats(stats_list: List[MatchStatsCreate], stage_id: int, db: Session = Depends(get_db),
                       _=Depends(auth_admin)):
    stats_crud.create_match_stats_list(stats_list, stage_id, db)
    return Response(status_code=202)
