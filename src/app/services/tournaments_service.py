from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import List, Tuple, Optional, Dict

import pytz
from sqlalchemy.orm import Session

from src.app.crud import tournaments as tournaments_crud
from src.app.crud.stages import get_stages, get_stage_by_id, create_stages
from src.app.crud.stats import create_match_stats_list, create_tournament_stats, get_tournament_stats, edit_global_stats
from src.app.crud.user import user_id_by_team
from src.app.database.db import SessionLocal
from src.app.exceptions.tournament_exceptions import StageMustBeEmpty, TournamentAlreadyFinished, \
    StatsOfNotParticipatedTeam, WrongTournamentDates
from src.app.models.games import Games
from src.app.models.stage import Stage
from src.app.models.stats import MatchStats, TournamentStats
from src.app.models.tournament import Tournament
from src.app.models.tournament_states import States
from src.app.schemas.stats import TournamentStatsCreate, GlobalStatsEdit
from src.app.schemas.tournaments import TournamentCreate
from src.app.schemas import stats as stats_schemas

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
    start_date = datetime(year=9999, month=1, day=1, tzinfo=pytz.UTC)
    end_date = datetime(year=1, month=1, day=1, tzinfo=pytz.UTC)
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


def create_tournament(tournament_create: TournamentCreate, db: Session) -> dict:
    tournament_create = set_tournament_dates(tournament_create.stages, tournament_create)
    now_moscow = datetime.now(pytz.timezone('Europe/Moscow'))
    if tournament_create.start_date < now_moscow or tournament_create.end_date < tournament_create.start_date:
        raise WrongTournamentDates()
    db_tournament = tournaments_crud.create_tournament(tournament_create, db)
    create_stages(tournament_create.stages, db_tournament.id, db)
    if not is_tournament_tvt(db_tournament):
        myscheduler.plan_task(get_tournament_task_id(TournamentEvents.START_TOURNAMENT, db_tournament.id),
                              db_tournament.start_date, start_battleroyale_tournament, [db_tournament.id])
        myscheduler.plan_task(get_tournament_task_id(TournamentEvents.START_STAGE, db_tournament.id),
                              db_tournament.start_date+timedelta(seconds=10), fill_next_stage_battleroyale, [db_tournament.id])
    return {"tournament_id": db_tournament.id}


def find_active_stage(tournament_id: int, db: Session) -> Tuple[Optional[Stage], Optional[Stage], bool]:
    """ returns active stage, previous stage, and bool = (is stage last)"""
    sorted_stages = get_stages(tournament_id, db)
    stages_count = len(sorted_stages)
    for i in range(stages_count):
        if not sorted_stages[i].finished:
            if i == 0:
                return sorted_stages[i], None, (i == stages_count-1)
            return sorted_stages[i], sorted_stages[i-1], (i == stages_count-1)
    return None, None, False


def pause_tournament(tournament_id: int, db: Session):
    tstart_task_id = get_tournament_task_id(TournamentEvents.START_TOURNAMENT, tournament_id)
    sstart_task_id = get_tournament_task_id(TournamentEvents.START_STAGE, tournament_id)
    if myscheduler.task_exists(tstart_task_id):
        myscheduler.remove_task(tstart_task_id)
    if myscheduler.task_exists(sstart_task_id):
        myscheduler.remove_task(sstart_task_id)
    tournaments_crud.update_tournament_state(States.PAUSED, tournament_id, db)


def kick_player_from_tournament(user_email: str, tournament_id: int, db: Session):
    tournaments_crud.remove_tournament_player(tournament_id, user_email, db)


def register_in_tournament(user_email: str, tournament_id: int, db: Session):
    tournaments_crud.add_user_to_tournament(tournament_id, user_email, db)


def upload_stats(stage_id: int, stats: List[stats_schemas.MatchStatsCreate], db: Session):
    stage = get_stage_by_id(stage_id, db)
    teams = set(stage.teams)
    for stat in stats:
        if stat.team_name not in teams:
            raise StatsOfNotParticipatedTeam()
    create_match_stats_list(stats, stage_id, db)


def save_tournament_stats(stats: Dict[str, Tuple[int, int, int]], tournament_id: int, db: Session, commit=True):
    db_stats_list = get_tournament_stats(tournament_id, db)
    for db_stats in db_stats_list:
        team_name = db_stats.user.team_name
        if team_name in stats:
            db_stats.score += stats[team_name][0]
            db_stats.kills_count += stats[team_name][1]
            db_stats.wins_count += stats[team_name][2]
        else:
            print(f"[NOT ERROR, BUT INFO] team {team_name} exists in tournament list, but not found in stage stats")
        db.add(db_stats)
    if commit:
        db.commit()


# ---------------------- BATTLEROYALE ONLY -----------------------
def start_battleroyale_tournament(tournament_id: int):
    db = SessionLocal()
    tournament = tournaments_crud.get_tournament(tournament_id, db)
    if len(tournament.users) < tournament.max_squads:
        tournaments_crud.update_tournament_state(States.PAUSED, tournament_id, db)
        print("the number of registered players is less than required, the tournament is paused")
        db.close()
        return
    tournaments_crud.update_tournament_state(States.IS_ON, tournament_id, db)
    create_empty_tournament_stats(tournament, db)
    db.close()


def end_battleroyale_tournament(tournament_id: int, last_stage: Stage, db: Session):
    tournaments_crud.update_tournament_state(States.FINISHED, tournament_id, db)
    _, summary_score = match_players_stats(last_stage.matches, False)
    save_tournament_stats(summary_score, tournament_id, db, False)
    db.commit()
    tournament_stats_list = get_tournament_stats(tournament_id, db)
    for stats in tournament_stats_list:
        gl_stat_new = GlobalStatsEdit(score=stats.score, kills_count=stats.kills_count, wins_count=stats.wins_count)
        edit_global_stats(gl_stat_new, stats.user_id, db, False)
    db.commit()


def create_empty_tournament_stats(tournament, db):
    for user in tournament.users:
        stats = TournamentStats(
            game=tournament.game,
            kills_count=0,
            score=0,
            user_id=user.id,
            tournament_id=tournament.id
        )
        db.add(stats)
    db.commit()


def match_players_stats(stats_list: List[MatchStats], winners_list=True) -> Tuple[Optional[List[str]],
                                                                                  Dict[str, Tuple[int, int, int]]]:
    """
    BATTLEROYALE GAMES ONLY!\n
    return list of players past in next stage and full list of user stats
    """
    summary_score = {}
    for stats in stats_list:
        if stats.user_id in summary_score:
            summary_score[stats.user.team_name][0] += stats.score
            summary_score[stats.user.team_name][1] += stats.kills_count
            summary_score[stats.user.team_name][2] += stats.placement == 1
        else:
            summary_score[stats.user.team_name] = (stats.score, stats.kills_count, int(stats.placement == 1))
    if winners_list:
        winners_raw = sorted(summary_score.items(), key=lambda x: x[1][0], reverse=True)[0:len(summary_score)//2+1]
        return list(map(lambda x: x[0], winners_raw)), summary_score
    return None, summary_score


def fill_next_stage_battleroyale(tournament_id: int, db: Session = None):
    """BATTLEROYALE GAMES ONLY!"""
    if db is None:
        db = SessionLocal()
    stage, previous_stage, _ = find_active_stage(tournament_id, db)
    if stage is None:
        raise TournamentAlreadyFinished(tournament_id)
    if len(stage.matches) > 0:
        raise StageMustBeEmpty(stage.id)
    if previous_stage in None:
        tournament = tournaments_crud.get_tournament(tournament_id, db)
        for user in tournament.users:
            stage.teams.append(user.team_name)
    else:
        stage.teams, summary_score = match_players_stats(previous_stage.matches)
        save_tournament_stats(summary_score, tournament_id, db, False)
        previous_stage.finished = True

    db.add(stage)
    db.add(previous_stage)
    db.commit()
    db.close()


def end_active_stage_battleroyale(tournament_id: int, db: Session):
    """BATTLEROYALE GAMES ONLY!"""
    stage, _, last = find_active_stage(tournament_id, db)
    if stage is None:
        raise TournamentAlreadyFinished(tournament_id)
    stage.finished = True
    if last:
        end_battleroyale_tournament(tournament_id, stage, db)
        return

    db.add(stage)
    db.commit()
    fill_next_stage_battleroyale(tournament_id, db)


# ---------------------- TVT ONLY -----------------------
def start_next_stage_tvt(tournament_id):
    """TVT GAMES ONLY!"""
    db = SessionLocal()
    tournament = tournaments_crud.get_tournament(tournament_id, db)
