from datetime import datetime, timedelta
from enum import Enum
import random
from typing import Tuple, Optional
from loguru import logger
from sqlalchemy.orm import Session

from src.app.crud.user import get_user_by_team
from src.app.database.db import SessionLocal
from src.app.exceptions.tournament_exceptions import MapChoiceDataNotFound, GameNotFoundInTvtPool
from src.app.models.games import Games
from src.app.models.tvt.match import TvtMatch
from src.app.schemas.tvt.map_choice_data import MapChoiceData
from src.app.services.redis_service import redis_client
from src.app.services.schedule_service import myscheduler
from src.app.services.tvt import tournaments_service as tvt_service


class MapChoiceManager:
    TIME_TO_CHOICE_SECONDS = 30

    class GameMaps(Enum):
        CSGO = {'dust 2', 'another map', 'another map2', 'another map3'}
        VALORANT = {'valorant map', 'another map', 'another map2', 'another map3'}

    def __init__(self, match_id: int, team: str):
        self.match_id = match_id
        self.key = f'tournament:map_choice:{match_id}'
        self.team = team
        self.last_data: Optional[MapChoiceData] = None

    def is_me_active(self):
        if self.last_data is None:
            self.update_data()
        return self.last_data .active_team == self.team

    def ban_map(self, map_name: str):
        if not self.is_me_active():
            logger.error('[lobby selector] user is inactive, but tries to ban map')
            return True
        self.update_data()
        if map_name not in self.last_data.maps:
            logger.error('[lobby selector] map already banned')
            return False
        self.last_data.maps.remove(map_name)
        if self.is_ended():
            self.__end_all()
            self.__synchronise_data()
            return True
        users_set = list(self.last_data.teams)
        users_set.remove(self.team)
        self.last_data.active_team = users_set[0]
        self.__synchronise_data()
        MapChoiceManager.plan_force_random_choice(self.match_id, self.last_data.active_team)
        return True

    def __end_all(self):
        db: Session = SessionLocal()
        user = get_user_by_team(self.team, db)
        t_id = db.query(TvtMatch).filter(TvtMatch.id == self.match_id).first().teams_stats[0].tournament_id
        tvt_service.remove_from_wait_room(user.email, t_id)
        tvt_service.check_users_remained(t_id)
        db.close()

    def is_ended(self) -> bool:
        if self.last_data is None:
            return False
        return len(self.last_data.maps) <= 1

    def get_data(self) -> MapChoiceData:
        if self.last_data is None:
            self.update_data()
        return self.last_data

    def get_row_data(self) -> str:
        if self.last_data is None:
            self.update_data()
        print(self.last_data.json())
        return self.last_data.json()

    def update_data(self):
        redis_str = redis_client.get_val(self.key)
        if redis_str is None:
            raise MapChoiceDataNotFound()
        self.last_data = MapChoiceData.parse_raw(redis_str.decode('ascii'))

    def __synchronise_data(self):
        if self.last_data is None:
            return
        redis_client.add_val(self.key, self.last_data.json())

    @staticmethod
    def get_maps_by_game(game: Games) -> GameMaps:
        if game == Games.CSGO:
            return MapChoiceManager.GameMaps.CSGO
        elif game == Games.VALORANT:
            return MapChoiceManager.GameMaps.VALORANT
        raise GameNotFoundInTvtPool()

    @staticmethod
    def create_lobby(match_id: int, game: GameMaps, teams: Tuple[str, str]):
        exp = datetime.now() + timedelta(seconds=MapChoiceManager.TIME_TO_CHOICE_SECONDS)
        data = MapChoiceData(teams=teams, maps=game.value, active_team=teams[0], switch_time=exp)
        key = f'tournament:map_choice:{match_id}'
        redis_client.add_val(key, data.json(), timedelta(minutes=10))
        MapChoiceManager.plan_force_random_choice(match_id, data.active_team)

    @staticmethod
    def plan_force_random_choice(match_id: int, now_active_team: str):
        key = f'tournament:map_choice:{match_id}'
        if myscheduler.task_exists(key):
            myscheduler.remove_task(key)
        exp = datetime.now() + timedelta(seconds=MapChoiceManager.TIME_TO_CHOICE_SECONDS + 1)
        myscheduler.plan_task(key, exp, MapChoiceManager.random_choice, [match_id, now_active_team], 3)

    @staticmethod
    def random_choice(match_id: int, team: str):
        manager = MapChoiceManager(match_id, team)
        if not manager.is_me_active():
            logger.error('[lobby selector] force random map choice must be deleted, because user was changed')
            return
        data = manager.get_data()
        rmap = random.choice(list(data.maps))
        if not manager.ban_map(rmap):
            logger.error(f'[lobby selector] cant ban map in force auto-ban method ({match_id})')
