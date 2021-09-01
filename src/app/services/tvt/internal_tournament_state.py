from datetime import timedelta
from enum import Enum

from src.app.services.redis_service import redis_client


class TournamentInternalStateManager:

    class State(Enum):
        WAITING = "WA"
        CONNECTING = "CO"
        ADMIN_MANAGEMENT = "AM"
        MAP_CHOICE = "MC"
        VERIFYING_RESULTS = "VR"

    @staticmethod
    def __get_key(t_id: int):
        return f'tournament:{t_id}:internal_state'

    @staticmethod
    def set_state(tournament_id: int, state: State):
        exp = timedelta(days=1)
        if state == TournamentInternalStateManager.State.MAP_CHOICE:
            exp = timedelta(minutes=10)
        redis_client.add_val(TournamentInternalStateManager.__get_key(tournament_id), state.value, exp)

    @staticmethod
    def get_state(tournament_id: int):
        state_val = redis_client.get_val(TournamentInternalStateManager.__get_key(tournament_id))
        if state_val is None:
            return TournamentInternalStateManager.State.WAITING
        state_val = state_val.encode('utf-8')
        return TournamentInternalStateManager.State(state_val)
