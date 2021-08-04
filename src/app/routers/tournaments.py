from typing import List, Optional

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from src.app.crud import tournaments as tournaments_crud
from src.app.exceptions.tournament_exceptions import NotAllowedForTVT
from src.app.models.games import Games
from src.app.models.tournament_states import States
from src.app.schemas.token_data import TokenData
from src.app.schemas.tournaments import TournamentCreate, TournamentPreview, Tournament
from src.app.services.auth import auth_admin, try_auth_user, auth_user
from src.app.utils import get_db
from src.app.services import tournaments_service

router = APIRouter(
    prefix="/api/v2/tournaments",
    tags=["tournaments"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[TournamentPreview])
def get_tournaments_previews(game: Optional[Games], db: Session = Depends(get_db),
                             auth: Optional[TokenData] = Depends(try_auth_user)):
    tournaments: List[TournamentPreview] = tournaments_crud.get_tournaments(game, db)
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
def get_tournament(db: Session = Depends(get_db)):
    return tournaments_crud.get_tournaments_count(db)


@router.post("/", response_model=dict)
def create_tournament(tournament: TournamentCreate, db: Session = Depends(get_db), _=Depends(auth_admin)):
    return tournaments_service.create_tournament(tournament, db)


@router.delete("/")
def delete_tournament(tournament_id: int, db: Session = Depends(get_db), _=Depends(auth_admin)):
    tournaments_crud.remove_tournament(tournament_id, db)


@router.get("/register", response_model=dict)
def create_tournament(tournament_id: int, db: Session = Depends(get_db), user_data: TokenData = Depends(auth_user)):
    tournaments_service.register_in_tournament(user_data.email, tournament_id, db)


@router.get("/unregister", response_model=dict)
def create_tournament(tournament_id: int, db: Session = Depends(get_db), user_data: TokenData = Depends(auth_user)):
    tournaments_service.kick_player_from_tournament(user_data.email, tournament_id, db)


@router.get("/pause")
def pause_tournament(tournament_id: int, db: Session = Depends(get_db), _=Depends(auth_admin)):
    tournaments_crud.update_tournament_state(States.PAUSED, tournament_id, db)
