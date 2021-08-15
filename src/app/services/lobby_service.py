from typing import List, Dict
from src.app.models.lobbies import Lobby
from src.app.schemas.stats import LiteMatchStats, MatchStatsFrontend


def convert_to_array(data: Dict[str, dict]):
    result = []
    for team in data.keys():
        result.append(MatchStatsFrontend(name=team, overallScore=data[team]["sum"], matches=data[team]["matches"]))
    return result


def convert_lobby_to_frontend_ready(lobby: Lobby, team_name: str):
    teams = {}
    lobby_key = ''
    for match in lobby.stats:
        team_name = match.user.team_name
        if team_name in teams:
            teams[team_name]["sum"] += match.score
            teams[team_name]["matches"].append(LiteMatchStats.from_orm(match))
        else:
            ready_stat = {"sum": match.score, "matches": [LiteMatchStats.from_orm(match)]}
            teams[team_name] = ready_stat
    if team_name in teams:
        lobby_key = lobby.key
    return convert_to_array(teams), lobby_key


def convert_lobbies_to_frontend_ready(lobbies: List[Lobby], team_name: str):
    if lobbies is None:
        return [], -1
    ready_lobbies = []
    final_lobby_key = ''
    for lobby in lobbies:
        ready_lobby, lobby_key = convert_lobby_to_frontend_ready(lobby, team_name)
        ready_lobbies.append({'id': lobby.id, 'teams': ready_lobby})
        if lobby_key != '':
            final_lobby_key = lobby_key
    return ready_lobbies, final_lobby_key
