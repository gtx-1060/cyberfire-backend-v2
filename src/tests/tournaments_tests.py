from datetime import timedelta, datetime
from typing import Tuple

import pytz
from fastapi.testclient import TestClient
from uuid import uuid4, uuid1

from src.app.main import app
from src.app.models.games import Games
from src.app.schemas.lobbies import LobbyCreate
from src.app.schemas.stats import MatchStatsCreate
from src.app.schemas.user import UserCreate

client = TestClient(app)
players_count = 30

tournament = {
    "title": "string",
    "description": "string",
    "rewards": [
        "string"
    ],
    "stages": [
        {
            "title": "s1",
            "description": "string",
            "stage_datetime": datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(seconds=30),
            "lobbies": []
        },
        {
            "title": "s2",
            "description": "string",
            "stage_datetime": datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(minutes=10),
            "lobbies": []
        }
    ],
    "stream_url": "string",
    "game": "apex",
    "max_squads": players_count,
    "start_date": "2021-08-12T19:57:25.098Z",
    "end_date": "2021-08-12T19:57:25.098Z"
}


def register(cl: TestClient) -> UserCreate:
    data = UserCreate(password=str(uuid1()), email=str(uuid4()), username=str(uuid1()), team_name=str(uuid4()))
    r = cl.post('/api/v2/users/register', data=data.json())
    assert r.status_code == 202 or r.status_code == 200
    return data


def login(cl: TestClient, user: UserCreate) -> str:
    data = {'username': user.email, 'password': user.password}
    r = cl.post('/api/v2/users/login', data=data)
    assert r.status_code == 200
    assert 'access_token' in r.json()
    return r.json()['access_token']


def create_tournament(cl: TestClient, token: str) -> int:
    headers = {'Authorization': f"bearer {token}"}
    r = cl.post("/api/v2/tournaments", json=tournament, headers=headers)
    assert r.status_code == 200 or r.status_code == 202
    assert 'id' in r.json()
    return r.json()['id']


def register_to_tournament(cl: TestClient, token: str, t_id: int):
    headers = {'Authorization': f"bearer {token}"}
    r = cl.get(f'/api/v2/tournaments/register?tournament_id={t_id}', headers=headers)
    assert r.status_code == 200


def create_lobby(cl: TestClient, token: str, s_id: int):
    headers = {'Authorization': f"bearer {token}"}
    lobby = LobbyCreate(matches_count=3, stage_id=s_id)
    r = cl.post(f'/api/v2/tournaments/lobbies', headers=headers, json=lobby.json())
    assert r.status_code == 200 or r.status_code == 202


def create_stats(cl: TestClient, token: str, team_name: str, l_id: int):
    headers = {'Authorization': f"bearer {token}"}
    stats = MatchStatsCreate(
        kills_count=123,
        score=13,
        team_name=team_name,
        index=0,
        placement=1,
        game=Games.CSGO
    )
    r = cl.post(f'/api/v2/stats/match?lobby_id={l_id}', headers=headers, json=stats.json())
    assert r.status_code == 200 or r.status_code == 202


def test_tournament():
    """
    1 создать турнир \n
    2 зарегистрировать n юзеров \n
    3 записать их на турнир \n
    4 добавить их в лобби \n
    5 начать стэйдж \n
    6 проверить стэйт турнира \n
    7 завершить стэйдж \n
    8 повторить 5-7 \n
    9 завершить турнир \n
    """

    user_dataset = []
    tokens = []
    for i in range(players_count):
        user_dataset += register(client)
        tokens += login(client, user_dataset[i])
