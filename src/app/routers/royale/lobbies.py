from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette.responses import Response

from src.app.crud.royale import lobbies as lobbies_crud
from src.app.schemas.royale.lobbies import Lobby, LobbyCreate, LobbyEdit
from src.app.services.auth_service import auth_admin

from src.app.utils import get_db

router = APIRouter(
    prefix="/api/v2/royale/lobbies",
    tags=["lobbies"],
    responses={404: {"description": "Not found"}},
)


@router.get('', response_model=Lobby)
def get_lobby(lobby_id: int, db: Session = Depends(get_db)):
    return lobbies_crud.get_lobby(lobby_id, db)


@router.post('', response_model=dict)
def add_lobby(lobby: LobbyCreate, db: Session = Depends(get_db), _=Depends(auth_admin)):
    db_lobby = lobbies_crud.create_lobby(lobby, db)
    return {"id": db_lobby.id}


@router.put('', response_model=dict)
def edit_lobby(lobby: LobbyEdit, lobby_id: int, db: Session = Depends(get_db), _=Depends(auth_admin)):
    db_lobby = lobbies_crud.edit_lobby(lobby, lobby_id, db)
    return {"id": db_lobby.id}


@router.delete('')
def remove_lobby(lobby_id: int, db: Session = Depends(get_db), _=Depends(auth_admin)):
    lobbies_crud.remove_lobby(lobby_id, db)
    return Response(status_code=200)
