from typing import Tuple

from fastapi.testclient import TestClient

from src.app.main import app


client = TestClient(app)


def register(cl: TestClient) -> Tuple[str, str]:
    client.post('/api/v2/users')


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

    pass