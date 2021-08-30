from typing import List, Optional
from fastapi import APIRouter, UploadFile
from fastapi.params import Depends, File
from sqlalchemy.orm import Session
from starlette.responses import Response

from src.app.config import OTHER_STATIC_PATH
from src.app.crud.tvt import tournaments as tournaments_crud
from src.app.crud.user import get_user_squad_by_team
from src.app.models.games import Games
from src.app.models.tournament_states import TournamentStates
from src.app.schemas.token_data import TokenData
from src.app.schemas.royale.tournaments import TournamentPreview
from src.app.schemas.tvt.stages import TvtStage
from src.app.schemas.tvt.tournaments import TvtTournamentCreate, TvtTournament, TvtTournamentEdit, \
    TvtTournamentAdvancedData
from src.app.services.auth_service import auth_admin, try_auth_user, auth_user
from src.app.utils import get_db, save_image, delete_image_by_web_path
from src.app.services.tvt import tournaments_service

router = APIRouter(
    prefix="/api/v2/tvt/tournaments",
    tags=["tournament team vs team"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=List[TournamentPreview])
def get_tournaments_previews(game: Games, db: Session = Depends(get_db), count=20, offset=0):
    return tournaments_crud.get_tournaments_tvt(game, offset, count, db)


@router.get("/advanced_data_list", response_model=List[TvtTournamentAdvancedData])
def is_user_tournaments_registered(game: Optional[Games] = None, count=20, offset=0, db: Session = Depends(get_db),
                                   auth: TokenData = Depends(auth_user)):
    tournaments = tournaments_crud.get_tournaments_tvt(game, offset, count, db)
    tournaments_registered: List[TvtTournamentAdvancedData] = []
    for tournament in tournaments:
        registered, register_access = tournaments_service.tournament_registrable_data_tvt(tournament.id, auth.email, db)
        tournaments_registered.append(TvtTournamentAdvancedData(registered=registered,
                                                                id=tournament.id, can_register=register_access))
    return tournaments_registered


@router.get("/advanced_data", response_model=TvtTournamentAdvancedData)
def get_tournament_advanced_data(tournament_id: int, db: Session = Depends(get_db),
                                 auth: TokenData = Depends(auth_user)):
    is_registered, register_access = tournaments_service.tournament_registrable_data_tvt(tournament_id, auth.email, db)
    return TvtTournamentAdvancedData(registered=is_registered, id=0, can_register=register_access)


@router.get("/by_id", response_model=TvtTournament)
def get_tournament(tournament_id: int, db: Session = Depends(get_db), _=Depends(try_auth_user)):
    tournament = TvtTournament.from_orm(tournaments_crud.get_tournament_tvt(tournament_id, db))
    for user in tournament.users:
        user.squad = get_user_squad_by_team(user.team_name, tournament.game, db)
    return tournament


@router.get("/count", response_model=int)
def get_tournaments_count(db: Session = Depends(get_db)):
    return tournaments_crud.get_tournaments_count_tvt(db)


@router.post("", response_model=dict)
def create_tournament(tournament: TvtTournamentCreate, db: Session = Depends(get_db), _=Depends(auth_admin)):
    return tournaments_service.create_tournament_tvt(tournament, db)


@router.delete("")
def delete_tournament(tournament_id: int, db: Session = Depends(get_db), _=Depends(auth_admin)):
    tournament = tournaments_crud.get_tournament_tvt(tournament_id, db)
    tournaments_crud.remove_tournament_tvt(tournament_id, db)
    tournaments_service.remove_tournament_tvt_jobs(tournament_id)
    delete_image_by_web_path(tournament.img_path)
    return Response(status_code=200)


@router.get("/register", response_model=dict)
def register_in_tournament(tournament_id: int, db: Session = Depends(get_db),
                           user_data: TokenData = Depends(auth_user)):
    tournaments_service.register_in_tournament(user_data.email, tournament_id, db)
    return Response(status_code=200)


@router.get("/unregister", response_model=dict)
def unregister_in_tournament(tournament_id: int, db: Session = Depends(get_db),
                             user_data: TokenData = Depends(auth_user)):
    tournaments_service.unregister_player_from_tournament(user_data.email, tournament_id, db)
    return Response(status_code=200)


@router.get("/kick")
def kick_user(tournament_id: int, team_name: str, db: Session = Depends(get_db), _=Depends(auth_admin)):
    tournaments_service.kick_player_from_tournament(team_name, tournament_id, db)
    return Response(status_code=200)


@router.post('/upload_image')
def upload_news_image(tournament_id: int, image: UploadFile = File(...), _=Depends(auth_admin),
                      db: Session = Depends(get_db)):
    old_web_path = tournaments_crud.get_tournament_tvt(tournament_id, db).img_path
    web_path = save_image(OTHER_STATIC_PATH, image.file.read())
    tournaments_edit = TvtTournamentEdit(img_path=web_path)
    tournaments_crud.edit_tournament_tvt(tournaments_edit, tournament_id, db)
    if old_web_path != '':
        delete_image_by_web_path(old_web_path)
    return Response(status_code=202)


@router.put('')
def edit_tournament(tournament: TvtTournamentEdit, tournament_id: int, _=Depends(auth_admin),
                    db: Session = Depends(get_db)):
    tournaments_crud.edit_tournament_tvt(tournament, tournament_id, db)
    return Response(status_code=200)


@router.get('/finish')
def finish_tournament(tournament_id: int, _=Depends(auth_admin), db: Session = Depends(get_db)):
    pass
    # TODO: JUST DO IT