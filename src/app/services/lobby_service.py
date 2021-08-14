from typing import List, Dict, Tuple

from sqlalchemy.orm import Session

from src.app.models.lobbies import Lobby
from src.app.schemas.stats import LiteMatchStats
from src.app.crud import lobbies as lobbies_crud


def convert_lobby_to_frontend_ready(lobby: Lobby) -> Dict[str, dict]:
    teams = {}
    for match in lobby.stats:
        team_name = match.user.team_name
        if team_name in teams:
            teams[team_name]["sum"] += match.score
            teams[team_name]["matches"].append(LiteMatchStats.from_orm(match))
        else:
            ready_stat = {"sum": match.score, "matches": [LiteMatchStats.from_orm(match)]}
            teams[team_name] = ready_stat
    return teams


def convert_lobbies_to_frontend_ready(lobbies: List[Lobby], user_team_name: str, get_key: bool, db: Session) \
        -> Tuple[List[Dict[str, dict]], str]:
    if lobbies is None:
        return [], ''
    ready_lobbies = []
    key = ''
    for lobby in lobbies:
        ready_lobby = convert_lobby_to_frontend_ready(lobby)
        ready_lobbies.append(ready_lobby)
        if get_key and key == '' and user_team_name != '' and user_team_name in ready_lobby:
            key = lobbies_crud.get_lobby(lobby.id, db).key
    return ready_lobbies, key
