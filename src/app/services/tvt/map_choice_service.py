from datetime import datetime, timedelta
from enum import Enum
import random
from typing import Tuple
from loguru import logger
from sqlalchemy.orm import Session

from src.app.crud.user import get_user_by_team
from src.app.database.db import SessionLocal
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
        self.__is_ended = False
        self.team = team

    def is_me_active(self):
        data = self.get_data()
        if data is None:
            return False
        return data.active_team == self.team

    def ban_map(self, map_name: str):
        if not self.is_me_active():
            logger.error('[lobby selector] user is inactive, but tries to ban map')
            return False
        data = self.get_data()
        if map_name not in data.maps:
            logger.error('[lobby selector] map already banned')
            return False
        data.maps.remove(map_name)
        if len(data.maps) == 1:
            self.__end_all()
            self.__save_data(data)
            return True
        users_set = list(data.teams)
        users_set.remove(self.team)
        data.active_team = users_set[0]
        self.__save_data(data)
        MapChoiceManager.plan_force_random_choice(self.match_id, data.active_team)
        return True

    def __end_all(self):
        self.__is_ended = True
        db: Session = SessionLocal()
        user = get_user_by_team(self.team, db)
        t_id = db.query(TvtMatch).filter(TvtMatch.id == self.match_id).first().teams_stats[0].tournament_id
        tvt_service.remove_from_wait_room(user.email, t_id)
        tvt_service.check_users_remained(t_id)
        db.close()

    def is_ended(self) -> bool:
        return self.__is_ended

    def get_data(self) -> MapChoiceData:
        redis_str = redis_client.get_val(self.key).encode('utf-8')
        return MapChoiceData.parse_raw(redis_str)

    def get_row_data(self) -> str:
        return redis_client.get_val(self.key).encode('utf-8')

    def __save_data(self, data: MapChoiceData):
        redis_client.add_val(self.key, data.json())

    @staticmethod
    def create_lobby(match_id: int, game: GameMaps, teams: Tuple[str, str]):
        exp = datetime.now() + timedelta(seconds=MapChoiceManager.TIME_TO_CHOICE_SECONDS)
        data = MapChoiceData(users=teams, maps=game.value, active_team=teams[0], switch_time=exp)
        key = f'tournament:map_choice:{match_id}'
        redis_client.add_val(key, data.json())
        MapChoiceManager.plan_force_random_choice(match_id, data.active_team)

    @staticmethod
    def plan_force_random_choice(match_id: int, now_active_team: str):
        key = f'tournament:map_choice:{match_id}'
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
