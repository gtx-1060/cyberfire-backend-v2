from datetime import timedelta, datetime

import pytz
from fastapi.testclient import TestClient
from uuid import uuid4

from src.app.main import app
from src.app.models.games import Games
from src.app.schemas.royale.lobbies import LobbyCreate
from src.app.schemas.royale.squad import Squad
from src.app.schemas.royale.stats import MatchStatsCreate
from src.app.schemas.user import UserCreate, UserEdit

client = TestClient(app)
players_count = 15
prefix = 'test2'

tournament = {
    "title": "hi",
    "description": "string",
    "rewards": [
        "string"
    ],
    "stages": [
        {
            "title": "s1",
            "description": "string",
            "stage_datetime": str(datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(seconds=120)),
            "lobbies": []
        },
        {
            "title": "s2",
            "description": "string",
            "stage_datetime": str(datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(minutes=10)),
            "lobbies": []
        }
    ],
    "stream_url": "string",
    "game": "apex",
    "max_squads": players_count,
    "start_date": "2021-08-12T19:57:25.098Z",
    "end_date": "2021-08-12T19:57:25.098Z"
}


def register(cl: TestClient, prefix: str, index: int) -> UserCreate:
    data = UserCreate(password=f'{prefix}_pass_{index}', email=f'{prefix}_mail@_{index}',
                      username='bot', team_name=str(uuid4())[0:12])
    r = cl.post('/api/v2/users/register', data=data.json())
    assert r.status_code == 202 or r.status_code == 200
    return data


def login(cl: TestClient, user: UserCreate) -> str:
    data = {'username': user.email, 'password': user.password}
    r = cl.post('/api/v2/users/login', data=data)
    assert r.status_code == 200
    assert 'access_token' in r.json()
    return r.json()['access_token']


def fill_squad(cl: TestClient, token: str):
    headers = {'Authorization': f"bearer {token}"}
    user = UserEdit(squads=[Squad(game=Games.APEX, players=['12', '12', '12'])])
    r = cl.put('/api/v2/users', data=user.json(), headers=headers)
    assert r.status_code == 200


def create_tournament(cl: TestClient, token: str) -> int:
    headers = {'Authorization': f"bearer {token}"}
    r = cl.post("/api/v2/tournaments", json=tournament, headers=headers)
    assert r.status_code == 200 or r.status_code == 202
    assert 'tournament_id' in r.json()
    return r.json()['tournament_id']


def register_to_tournament(cl: TestClient, token: str, t_id: int):
    headers = {'Authorization': f"bearer {token}"}
    r = cl.get(f'/api/v2/tournaments/register?tournament_id={t_id}', headers=headers)
    assert r.status_code == 200


def create_lobby(cl: TestClient, token: str, s_id: int):
    headers = {'Authorization': f"bearer {token}"}
    lobby = LobbyCreate(matches_count=3, stage_id=s_id, key="13131")
    r = cl.post(f'/api/v2/lobbies', headers=headers, data=lobby.json())
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
    r = cl.post(f'/api/v2/stats/match?lobby_id={l_id}', headers=headers, data=stats.json())
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
    admin = UserCreate(password='123456', email='123456@', username='123456', team_name='123456')
    admin_token = login(client, admin)
    t_id = create_tournament(client, admin_token)
    user_dataset = []
    tokens = []
    for i in range(players_count-1):
        user_dataset.append(register(client, prefix, i))
        tokens.append(login(client, user_dataset[i]))

    r = client.get(f'/api/v2/tournaments/by_id?tournament_id={t_id}')
    assert r.status_code == 200
    stage_id = r.json()['stages'][0]['id']
    assert stage_id is not None
    print(stage_id)

    for token in tokens:
        fill_squad(client, token)
        register_to_tournament(client, token, t_id)

    # lobby_tests(admin_token, stage_id, t_id, tokens, user_dataset)


# def lobby_tests(admin_token, stage_id, user_dataset):
#     create_lobby(client, admin_token, stage_id)
#     for user in user_dataset:
#         create_stats(client, admin_token, user.team_name, 1)
