from typing import List
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette.responses import Response

from src.app.crud.royale import stats as stats_crud
from src.app.crud.royale.lobbies import get_lobby
from src.app.crud.royale.stages import get_stage_by_id
from src.app.crud.user import get_user_by_email
from src.app.models.games import Games
from src.app.schemas.royale.stats import TournamentStats, GlobalStats, MatchStatsCreate, MatchStatsEdit
from src.app.schemas.token_data import TokenData
from src.app.services.auth_service import auth_admin, try_auth_user
from src.app.services.royale.lobby_service import convert_lobbies_to_frontend_ready, convert_lobby_to_frontend_ready
from src.app.services.royale.tournaments_service import save_row_stats
from src.app.utils import get_db

router = APIRouter(
    prefix="/api/v2/stats",
    tags=["stats"],
    responses={404: {"description": "Not found"}},
)


@router.get('/royale/stage', response_model=dict)
def get_math_stats(stage_id: int, user_data: TokenData = Depends(try_auth_user), db: Session = Depends(get_db)):
    stage = get_stage_by_id(stage_id, db)
    # костыль, тк при пустой строке, если в этапе находилась команда
    # с пустым названием, ей давался ключ от лобби
    user_team = '@!742731@!4124123'
    if user_data is not None:
        user_team = get_user_by_email(user_data.email, db).team_name
    data, lobby_key = convert_lobbies_to_frontend_ready(stage.lobbies, user_team)
    return {'lobbies': data, "key": lobby_key}


@router.get('/royale/lobby', response_model=dict)
def get_math_stats(lobby_id: int, user_data: TokenData = Depends(try_auth_user), db: Session = Depends(get_db)):
    lobby = get_lobby(lobby_id, db)
    user_team = ''
    if user_data is not None:
        user_team = get_user_by_email(user_data.email, db).team_name
    data, key = convert_lobby_to_frontend_ready(lobby, user_team)
    print(f'name:{user_team}')
    if data is None:
        return {'lobby': [], "key": ''}
    return {'lobby': data, "key": key}


@router.get('/royale/tournament', response_model=List[TournamentStats])
def get_tournament_stats(tournament_id: int, db: Session = Depends(get_db)):
    return stats_crud.get_tournament_stats(tournament_id, db)


@router.get('', response_model=List[GlobalStats])
def get_global_stats(game: Games, offset=0, count=20, db: Session = Depends(get_db)):
    db_stats = stats_crud.get_global_stats(game, offset, count, db)
    return db_stats


@router.post('/royale/matches')
def create_new_multiple_match_stats(stats_list: List[MatchStatsCreate], lobby_id: int,
                                    db: Session = Depends(get_db), _=Depends(auth_admin)):
    save_row_stats(stats_list, lobby_id, db)
    return Response(status_code=202)


@router.post('/royale/match')
def create_match_stats(stats: MatchStatsCreate, lobby_id: int, db: Session = Depends(get_db),
                       _=Depends(auth_admin)):
    get_lobby(lobby_id, db)
    stats_crud.create_match_stats(stats, lobby_id, db)
    return Response(status_code=202)


@router.put('/royale/match')
def edit_match_stats(match: MatchStatsEdit, match_id: int, db: Session = Depends(get_db),
                     _=Depends(auth_admin)):
    stats_crud.edit_match_stats(match, match_id, db)
    return Response(status_code=200)
