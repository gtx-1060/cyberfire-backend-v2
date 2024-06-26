from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette.responses import Response

from src.app.crud.royale.lobbies import remove_team
from src.app.crud.royale.stats import delete_match_by_lobby
from src.app.crud.royale import stages as stages_crud
from src.app.schemas.royale.stage import Stage, StagePreview, StageEdit, StageLeadersEdit
from src.app.services.auth_service import auth_admin, try_auth_user
from src.app.utils import get_db
from src.app.services.royale import tournaments_service

router = APIRouter(
    prefix="/api/v2/royale/stages",
    tags=["stages"],
    responses={404: {"description": "Not found"}},
)


@router.get('', response_model=List[StagePreview])
def get_stages_previews(tournament_id: int, db: Session = Depends(get_db)):
    return stages_crud.get_stages(tournament_id, db)


@router.get('/by_id', response_model=Stage)
def get_stage(stage_id: int, _=Depends(try_auth_user), db: Session = Depends(get_db)):
    return stages_crud.get_stage_by_id(stage_id, db)


@router.put('')
def edit_stage(stage: StageEdit, stage_id: int, db: Session = Depends(get_db), _=Depends(auth_admin)):
    stages_crud.edit_stage(stage, stage_id, db)
    if stage.stage_datetime is not None:
        tournaments_service.update_db_tournament_date(stage_id, db)
    return Response(status_code=200)


@router.put('/leaders')
def edit_leaders(leaders: StageLeadersEdit, stage_id: int, db: Session = Depends(get_db), _=Depends(auth_admin)):
    tournaments_service.update_stage_leaders(leaders, stage_id, db)
    return Response(status_code=200)


@router.delete('/match')
def remove_match_stats(lobby_id: int, team_name: str, db: Session = Depends(get_db), _=Depends(auth_admin)):
    delete_match_by_lobby(team_name, lobby_id, db)
    return Response(status_code=200)


@router.delete("/team")
def kick_team_from_stage(lobby_id: int, team_name: str, db: Session = Depends(get_db), _=Depends(auth_admin)):
    remove_team(lobby_id, team_name, db)
    return Response(status_code=200)


@router.get('/start')
def start_stage(stage_id: int, _=Depends(auth_admin), db: Session = Depends(get_db)):
    tournaments_service.start_stage(stage_id, db)
    return Response(status_code=202)


@router.get('/finish')
def finish_stage(stage_id: int, _=Depends(auth_admin), db: Session = Depends(get_db)):
    tournaments_service.end_stage(stage_id, db)
    return Response(status_code=202)
