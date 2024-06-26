import asyncio
from fastapi import Query, WebSocketDisconnect, WebSocket
from loguru import logger
from time import time

from src.app.crud.tvt.tournaments import users_last_ison_stage_match
from src.app.crud.user import get_user_by_email
from src.app.database.db import SessionLocal
from src.app.exceptions.tournament_exceptions import UserCantConnectHere
from src.app.models.user import User
from src.app.services.auth_service import decode_token
from src.app.services.tvt.internal_tournament_state import TournamentInternalStateManager
from src.app.services.tvt.map_choice_service import MapChoiceManager
from src.app.services.tvt import tournaments_service as tvt_service
from src.app.services.tvt.tournaments_service import is_user_skipped


async def websocket_lobby_selector(websocket: WebSocket, tournament_id: int = Query(..., alias="tournament_id"),
                                   token: str = Query(..., alias="token")):
    db = SessionLocal()
    data = decode_token(token)
    user = get_user_by_email(data.email, db)
    logger.info(f'[lobby selector] connecting {user.team_name}')
    if not tvt_service.user_can_connect_to_map_selector(user, tournament_id, db):
        raise UserCantConnectHere()
    db.close()
    await websocket.accept()
    logger.info(f'[lobby selector] connected {user.team_name}')
    try:
        await lobby_selector_lifecycle(websocket, user, tournament_id)
    except WebSocketDisconnect:
        logger.warning(f'[lobby selector] disconnected {user.team_name}')
        if TournamentInternalStateManager.get_state(tournament_id) == TournamentInternalStateManager.State.CONNECTING:
            tvt_service.remove_from_wait_room(user.email, tournament_id)


async def lobby_selector_lifecycle(socket: WebSocket, user: User, tournament_id: int):
    match_id = await waiting_for_start(socket, user, tournament_id)
    if match_id == -1:
        await socket.send_text('vach sopernik clown')
        await socket.close()
        return
    elif match_id == 0:
        await socket.send_text('match not found')
        await socket.close()
        return
    await selecting_map(socket, match_id, user)


async def waiting_for_start(socket: WebSocket, user: User, t_id: int):
    tvt_service.add_to_wait_room(user.email, t_id)
    logger.info(f'[lobby selector] added to wait-room {user.team_name}')
    t_state = TournamentInternalStateManager.get_state(t_id)
    while t_state != TournamentInternalStateManager.State.MAP_CHOICE:
        try:
            await asyncio.wait_for(socket.receive_text(), timeout=5)
        except asyncio.TimeoutError:
            pass
        t_state = TournamentInternalStateManager.get_state(t_id)
    if is_user_skipped(user.email, t_id):
        return -1
    db = SessionLocal()
    match = users_last_ison_stage_match(user.id, t_id, db)
    if not match:
        db.close()
        return 0
    db.close()
    return match.id


async def selecting_map(socket: WebSocket, match_id: int, user: User):
    manager = MapChoiceManager(match_id, user.team_name)
    while True:
        manager.update_data()
        await socket.send_text(manager.get_row_data())
        if manager.is_ended():
            await socket.send_text('kostayne virubai')
            await socket.close()
            break
        if manager.is_me_active():
            try:
                await ban_map(manager, socket)
            except asyncio.TimeoutError:
                logger.info(f'[lobby selector] timeout in match {match_id} {user.team_name}')
        else:
            while True:
                await asyncio.sleep(5)
                manager.update_data()
                if manager.is_me_active():
                    break


async def ban_map(manager: MapChoiceManager, socket: WebSocket):
    time_remained = MapChoiceManager.TIME_TO_CHOICE_SECONDS
    start_choice_time = time()
    while True:
        gamemap = await asyncio.wait_for(socket.receive_text(), timeout=time_remained)
        if manager.ban_map(gamemap):
            break
        await socket.send_text('wrong data')
        time_remained = MapChoiceManager.TIME_TO_CHOICE_SECONDS - (time() - start_choice_time)