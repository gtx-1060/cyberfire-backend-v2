from typing import List, Optional

from fastapi import APIRouter, UploadFile
from fastapi.params import Depends, File
from sqlalchemy.orm import Session
from starlette.responses import Response

from src.app.config import OTHER_STATIC_PATH
from src.app.crud import tournaments as tournaments_crud
from src.app.exceptions.tournament_exceptions import NotAllowedForTVT
from src.app.models.games import Games
from src.app.models.tournament_states import States
from src.app.schemas.token_data import TokenData
from src.app.schemas.tournaments import TournamentCreate, TournamentPreview, Tournament, TournamentEdit
from src.app.services.auth import auth_admin, try_auth_user, auth_user
from src.app.utils import get_db, save_image, delete_image_by_web_path
from src.app.services import tournaments_service

router = APIRouter(
    prefix="/api/v2/tournaments",
    tags=["tournaments"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=List[TournamentPreview])
def get_tournaments_previews(game: Optional[Games] = None, db: Session = Depends(get_db), count=20, offset=0,
                             auth: Optional[TokenData] = Depends(try_auth_user)):
    tournaments: List[TournamentPreview] = tournaments_crud.get_tournaments(game, offset, count, db)
    if auth is not None:
        for tournament in tournaments:
            tournament.is_player_registered = tournaments_crud.is_users_in_tournament(tournament.id, auth.email, db)
    return tournaments


@router.get("/by_id", response_model=Tournament)
def get_tournament(tournament_id: int, db: Session = Depends(get_db), auth: TokenData = Depends(try_auth_user)):
    tournament: Tournament = tournaments_crud.get_tournament(tournament_id, db)
    if auth is not None:
        tournament.is_player_registered = tournaments_crud.is_users_in_tournament(tournament.id, auth.email, db)
    return tournament


@router.get("/count", response_model=int)
def get_tournaments_count(db: Session = Depends(get_db)):
    return tournaments_crud.get_tournaments_count(db)


@router.post("", response_model=dict)
def create_tournament(tournament: TournamentCreate, db: Session = Depends(get_db), _=Depends(auth_admin)):
    return tournaments_service.create_tournament(tournament, db)


@router.delete("")
def delete_tournament(tournament_id: int, db: Session = Depends(get_db), _=Depends(auth_admin)):
    tournaments_crud.remove_tournament(tournament_id, db)
    return Response(status_code=200)


@router.get("/register", response_model=dict)
def register_in__tournament(tournament_id: int, db: Session = Depends(get_db), user_data: TokenData = Depends(auth_user)):
    tournaments_service.register_in_tournament(user_data.email, tournament_id, db)
    return Response(status_code=200)


@router.get("/unregister", response_model=dict)
def unregister_in_tournament(tournament_id: int, db: Session = Depends(get_db), user_data: TokenData = Depends(auth_user)):
    tournaments_service.kick_player_from_tournament(user_data.email, tournament_id, db)
    return Response(status_code=200)


@router.get("/pause")
def pause_tournament(tournament_id: int, db: Session = Depends(get_db), _=Depends(auth_admin)):
    tournaments_crud.update_tournament_state(States.PAUSED, tournament_id, db)
    return Response(status_code=200)


@router.post('/upload_image')
def upload_news_image(tournament_id: int, image: UploadFile = File(...), _=Depends(auth_admin),
                      db: Session = Depends(get_db)):
    old_web_path = tournaments_crud.get_tournament(tournament_id, db).img_path
    web_path = save_image(OTHER_STATIC_PATH, image.file.read())
    tournaments_edit = TournamentEdit(img_path=web_path)
    tournaments_crud.edit_tournament(tournaments_edit, tournament_id, db)
    if old_web_path != '':
        delete_image_by_web_path(old_web_path)
    return Response(status_code=202)


@router.put('')
def edit_tournament(tournament: TournamentEdit, tournament_id: int, _=Depends(auth_admin),
                    db: Session = Depends(get_db)):
    tournaments_crud.edit_tournament(tournament, tournament_id, db)
    return Response(status_code=200)
