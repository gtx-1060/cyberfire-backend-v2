from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette.responses import Response

from src.app.crud.stages import remove_team_from_stage
from src.app.crud.stats import delete_match_by_stage
from src.app.crud import stages as stages_crud
from src.app.crud.user import get_user_by_email
from src.app.exceptions.tournament_exceptions import NotAllowedForTVT
from src.app.schemas.stage import Stage, StagePreview, StageEdit
from src.app.schemas.token_data import TokenData
from src.app.schemas.tournaments import TournamentEdit
from src.app.services.auth import auth_admin, try_auth_user
from src.app.utils import get_db
from src.app.services.tournaments_service import is_stage_tvt, update_db_tournament_date

router = APIRouter(
    prefix="/api/v2/stages",
    tags=["stages"],
    responses={404: {"description": "Not found"}},
)


@router.get('', response_model=List[StagePreview])
def get_stages_previews(tournament_id: int, db: Session = Depends(get_db)):
    return stages_crud.get_stages(tournament_id, db)


@router.get('/by_id', response_model=Stage)
def get_stage(stage_id: int, user_data: TokenData = Depends(try_auth_user), db: Session = Depends(get_db)):
    stage: Stage = stages_crud.get_stage_by_id(stage_id, db)
    if user_data is None:
        stage.keys = []
        return stage
    user = get_user_by_email(user_data.email, db)
    if user.team_name not in stage.teams:
        stage.keys = []
    return stage


@router.put('')
def edit_stage(stage: StageEdit, stage_id: int, db: Session = Depends(get_db), _=Depends(auth_admin)):
    if is_stage_tvt(stage_id, db):
        raise NotAllowedForTVT()
    stages_crud.edit_stage(stage, stage_id, db)
    if stage.stage_datetime is not None:
        update_db_tournament_date(stage_id, db)
    return Response(status_code=202)


@router.delete('/match')
def remove_match_stats(stage_id: int, team_name: str, db: Session = Depends(get_db), _=Depends(auth_admin)):
    delete_match_by_stage(team_name, stage_id, db)
    return Response(status_code=200)


@router.delete("/team")
def kick_team_from_stage(stage_id: int, team_name: str, db: Session = Depends(get_db), _=Depends(auth_admin)):
    remove_team_from_stage(stage_id, team_name, db)
    return Response(status_code=200)
