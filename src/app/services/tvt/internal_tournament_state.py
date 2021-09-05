from datetime import timedelta, datetime
from enum import Enum

from src.app.services.redis_service import redis_client


class TournamentInternalStateManager:

    TIME_TO_CONNECT_AT_LAUNCH = timedelta(minutes=5)

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
        if state == TournamentInternalStateManager.State.VERIFYING_RESULTS:
            exp = timedelta(minutes=180)
        redis_client.add_val(TournamentInternalStateManager.__get_key(tournament_id), state.value, exp)

    @staticmethod
    def set_connect_to_waitroom_timer(tournament_id: int):
        launch_at = datetime.now() + TournamentInternalStateManager.TIME_TO_CONNECT_AT_LAUNCH
        redis_client.add_val(f'tournament_launch:{tournament_id}', launch_at.isoformat(), TournamentInternalStateManager.TIME_TO_CONNECT_AT_LAUNCH)
        return launch_at

    @staticmethod
    def get_connect_to_waitroom_time(tournament_id: int):
        time = redis_client.get_val(f'tournament_launch:{tournament_id}')
        if time is None:
            return ''
        return time.decode('ascii')

    @staticmethod
    def get_state(tournament_id: int):
        state_val = redis_client.get_val(TournamentInternalStateManager.__get_key(tournament_id))
        if state_val is None:
            return TournamentInternalStateManager.State.WAITING
        state_val = state_val.decode('ascii')
        return TournamentInternalStateManager.State(state_val)
