from typing import List
from fastapi import APIRouter, UploadFile
from fastapi.params import Depends, File
from sqlalchemy.orm import Session
from starlette.responses import Response

from src.app.config import DEFAULT_VERIFIED_PATH
from src.app.crud.tvt import stats as stats_crud
from src.app.crud.user import get_user_by_email
from src.app.exceptions.tournament_exceptions import TournamentInternalStateException
from src.app.schemas.token_data import TokenData
from src.app.schemas.tvt.team_stats import TvtStats
from src.app.services.auth_service import auth_admin, auth_user
from src.app.services.tvt.internal_tournament_state import TournamentInternalStateManager
from src.app.utils import get_db, delete_image_by_web_path
from src.app.services.tvt import tournaments_service

router = APIRouter(
    prefix="/api/v2/tvt/stats",
    tags=["stats team vs team"],
    responses={404: {"description": "Not found"}},
)


@router.post('/upload_proof_image')
def load_results_proof(tournament_id: int, image: UploadFile = File(...), auth_data: TokenData = Depends(auth_user),
                       db: Session = Depends(get_db)):
    istate = TournamentInternalStateManager.get_state(tournament_id)
    user = get_user_by_email(auth_data.email, db)
    if istate != TournamentInternalStateManager.State.VERIFYING_RESULTS:
        raise TournamentInternalStateException()
    tournaments_service.load_match_results_proof(image, user, tournament_id, db)
    return Response(status_code=200)


@router.get('/not_verified', response_model=List[TvtStats])
def get_not_verified_stats(tournament_id: int, _=Depends(auth_admin), db: Session = Depends(get_db)):
    return stats_crud.load_not_verified_stats(tournament_id, db)


@router.get('/verify')
def load_results_proof(stats_id: int, score: int, _=Depends(auth_admin), db: Session = Depends(get_db)):
    stats = stats_crud.get_stats(stats_id, db)
    delete_image_by_web_path(stats.proof_path)
    stats_crud.edit_stats(stats_id, score, True, DEFAULT_VERIFIED_PATH, db)
    return Response(status_code=200)
