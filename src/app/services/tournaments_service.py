from datetime import datetime, timedelta
from enum import Enum
from typing import List, Tuple, Optional

from sqlalchemy.orm import Session

from src.app.crud import tournaments as tournaments_crud
from src.app.crud.stages import get_stages, get_stage_by_id
from src.app.crud.stats import get_match_stats
from src.app.database.db import SessionLocal
from src.app.exceptions.tournament_exceptions import StageMustBeEmpty
from src.app.models.games import Games
from src.app.models.stage import Stage
from src.app.models.stats import MatchStats
from src.app.models.tournament import Tournament
from src.app.models.tournament_states import States
from src.app.schemas.tournaments import TournamentCreate

# list of all tvt games
from src.app.services.schedule_service import myscheduler

tvt_games = {Games.CSGO, Games.VALORANT}


class TournamentEvents(Enum):
    START_TOURNAMENT = 'tournament_tournament'
    START_STAGE = 'tournament_next_stage'


def get_tournament_task_id(event: TournamentEvents, tournament_id: int):
    return f"{event.value}_{tournament_id}"


def is_tournament_tvt(tournament: Tournament) -> bool:
    return tournament.game in tvt_games


def is_stage_tvt(stage_id: int, db: Session) -> bool:
    db_stage = get_stage_by_id(stage_id, db)
    return is_tournament_tvt(db_stage.tournament)


def set_tournament_dates(stages, tournament) -> Tournament:
    start_date = datetime(year=9999, month=1, day=1)
    end_date = datetime(year=1, month=1, day=1)
    for stage in stages:
        if start_date > stage.stage_datetime:
            start_date = stage.stage_datetime
        if end_date < stage.stage_datetime:
            end_date = stage.stage_datetime
    tournament.start_date = start_date
    tournament.end_date = end_date
    return tournament


def update_db_tournament_date(stage_id: int, db: Session):
    tournament_id = get_stage_by_id(stage_id, db).tournament_id
    tournament = tournaments_crud.get_tournament(tournament_id, db)
    tournament = set_tournament_dates(get_stages(tournament_id, db), tournament)
    db.add(tournament)
    db.commit()


def create_tournament(tournament: TournamentCreate, db: Session) -> dict:
    tournament = set_tournament_dates(tournament.stages, tournament)
    tournament_id = tournaments_crud.create_tournament(tournament, db).id
    myscheduler.plan_task(get_tournament_task_id(TournamentEvents.START_TOURNAMENT, tournament_id),
                          tournament.start_date, start_tournament, [tournament_id])
    myscheduler.plan_task(get_tournament_task_id(TournamentEvents.START_STAGE, tournament_id),
                          tournament.start_date+timedelta(seconds=10), start_tournament, [tournament_id])
    return {"tournament_id": tournament_id}


def start_tournament(tournament_id):
    db = SessionLocal()
    tournaments_crud.update_tournament_state(States.IS_ON, tournament_id, db)
    db.close()


def find_active_stage(tournament_id: int, db: Session) -> Tuple[Stage, Optional[Stage]]:
    sorted_stages = get_stages(tournament_id, db)
    for i in range(len(sorted_stages)):
        if not sorted_stages[i].finished:
            if i == 0:
                return sorted_stages[i], None
            return sorted_stages[i], sorted_stages[i-1]


# def get_stage_teams(stats_list: List[MatchStats], db: Session) -> List[str]:
#     team_names = set()
#     for stats in stats_list:
#         team_names.add(stats.user.team_name)
#     return list(team_names)  # cash it for better performance


# ---------------------- BATTLEROYALE ONLY -----------------------
def get_winners(stats_list: List[MatchStats]) -> List[str]:
    """BATTLEROYALE GAMES ONLY!"""
    summary_score = {}
    for stats in stats_list:
        if stats.user_id in summary_score:
            summary_score[stats.user.team_name] += stats.score
        else:
            summary_score[stats.user.team_name] = stats.score
    winners_raw = sorted(summary_score.items(), key=lambda x: x[1], reverse=True)[0:len(summary_score)//2+1]
    return list(map(lambda x: x[0], winners_raw))


def fill_next_stage_battleroyale(tournament_id: int):
    """BATTLEROYALE GAMES ONLY!"""
    db = SessionLocal()
    stage, previous_stage = find_active_stage(tournament_id, db)
    if len(stage.matches) > 0:
        raise StageMustBeEmpty(stage.id)
    if previous_stage in None:
        tournament = tournaments_crud.get_tournament(tournament_id, db)
        for user in tournament.users:
            stage.teams.append(user.team_name)
    else:
        stage.teams = get_winners(previous_stage.matches)
        previous_stage.finished = True
    db.add(stage)
    db.add(previous_stage)
    db.commit()
    db.close()


# ---------------------- TVT ONLY -----------------------
def start_next_stage(tournament_id):
    """TVT GAMES ONLY!"""
    db = SessionLocal()
    tournament = tournaments_crud.get_tournament(tournament_id, db)
    pass
