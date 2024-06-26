from datetime import datetime
from enum import Enum
from functools import reduce
from typing import List, Tuple, Dict
import pytz
from sqlalchemy.orm import Session

from src.app.crud.royale import tournaments as tournaments_crud
from src.app.crud.royale.lobbies import get_lobby
from src.app.crud.royale.stages import get_stages, get_stage_by_id, create_stages, update_stage_state
from src.app.crud.royale.stats import create_match_stats_list, get_tournament_stats, edit_global_stats
from src.app.crud.user import get_user_squad_by_email, get_user_by_email, get_user_by_team
from src.app.database.db import SessionLocal
from src.app.exceptions.tournament_exceptions import WrongTournamentDates, NotEnoughPlayersInSquad, \
    AllStagesMustBeFinished, \
    WrongTournamentState, UserNotRegistered, MaxSquadsCount, UserAlreadyRegistered, StageAlreadyFinished, \
    TournamentAlreadyFinished
from src.app.middleware.log_middleware import access_logger, debug_logger
from src.app.models.games import Games, game_squad_sizes
from src.app.models.royale.stage import Stage
from src.app.models.royale.stats import MatchStats, TournamentStats
from src.app.models.royale.tournament import Tournament
from src.app.models.tournament_events import TournamentEvents
from src.app.models.tournament_states import TournamentStates, StageStates
from src.app.schemas.royale.stage import StageLeadersEdit
from src.app.schemas.royale.stats import GlobalStatsEdit, MatchStatsCreate
from src.app.schemas.royale.tournaments import TournamentCreate

# list of all tvt games
from src.app.services.schedule_service import myscheduler

tvt_games = {Games.CSGO, Games.VALORANT}


def get_tournament_task_id(event: TournamentEvents, tournament_id: int):
    return f"{event.value}_{tournament_id}"


def is_tournament_tvt(tournament: Tournament) -> bool:
    return tournament.game in tvt_games


def is_stage_tvt_by_id(stage_id: int, db: Session) -> bool:
    db_stage = get_stage_by_id(stage_id, db)
    return is_tournament_tvt(db_stage.tournament)


def is_stage_tvt(stage: Stage) -> bool:
    return is_tournament_tvt(stage.tournament)


def set_tournament_dates(stages, tournament) -> Tournament:
    start_date = datetime(year=9999, month=1, day=1, tzinfo=pytz.UTC)
    end_date = datetime(year=1, month=1, day=1, tzinfo=pytz.UTC)
    for stage in stages:
        if start_date.timestamp() > stage.stage_datetime.timestamp():
            start_date = stage.stage_datetime
        if end_date.timestamp() < stage.stage_datetime.timestamp():
            end_date = stage.stage_datetime
    tournament.start_date = start_date
    tournament.end_date = end_date
    return tournament


def update_db_tournament_date(stage_id: int, db: Session):
    tournament_id = get_stage_by_id(stage_id, db).tournament_id
    tournament = tournaments_crud.get_tournament_royale(tournament_id, db)
    tournament = set_tournament_dates(get_stages(tournament_id, db), tournament)
    now_moscow = datetime.now(pytz.timezone('Europe/Moscow'))
    if tournament.start_date.timestamp() > now_moscow.timestamp():
        tournament.state = TournamentStates.REGISTRATION
        schedule_tournament(tournament, db, False)
    db.add(tournament)
    db.commit()


def create_tournament(tournament_create: TournamentCreate, db: Session) -> dict:
    tournament_create = set_tournament_dates(tournament_create.stages, tournament_create)
    now_moscow = datetime.now(pytz.timezone('Europe/Moscow'))
    if tournament_create.start_date.timestamp() < now_moscow.timestamp() \
            or tournament_create.end_date.timestamp() < tournament_create.start_date.timestamp():
        raise WrongTournamentDates(tournament_create.start_date)
    db_tournament = tournaments_crud.create_tournament_royale(tournament_create, db)
    create_stages(tournament_create.stages, db_tournament.id, db)
    schedule_tournament(db_tournament, db)
    return {"tournament_id": db_tournament.id}


def schedule_tournament(db_tournament: Tournament, db: Session, autoremove=True):
    try:
        remove_tournament_jobs(db_tournament.id)
        myscheduler.plan_task(get_tournament_task_id(TournamentEvents.START_TOURNAMENT, db_tournament.id),
                              db_tournament.start_date, start_battleroyale_tournament, [db_tournament.id])
    except Exception as e:
        if autoremove:
            tournaments_crud.remove_tournament_royale(db_tournament.id, db)
        raise e


def remove_tournament_jobs(tournament_id):
    tstart_task_id = get_tournament_task_id(TournamentEvents.START_TOURNAMENT, tournament_id)
    if myscheduler.task_exists(tstart_task_id):
        myscheduler.remove_task(tstart_task_id)


def pause_tournament(tournament_id: int, db: Session):
    remove_tournament_jobs(tournament_id)
    tournaments_crud.update_tournament_state_royale(TournamentStates.PAUSED, tournament_id, db)


def __add_user_to_tournament(tournament_id: int, user_email: str, db: Session):
    user = get_user_by_email(user_email, db)
    tournament = tournaments_crud.get_tournament_royale(tournament_id, db)
    if tournament.state != TournamentStates.REGISTRATION:
        raise WrongTournamentState()
    if user in tournament.users:
        raise UserAlreadyRegistered(user_email)
    if len(tournament.users) < tournament.max_squads:
        tournament.users.append(user)
    else:
        raise MaxSquadsCount()
    db.add(tournament)
    db.commit()


def __remove_tournament_player(tournament_id: int, user_email: str, db: Session):
    user = get_user_by_email(user_email, db)
    tournaments_crud.remove_user_from_tournament_royale(user.id, tournament_id, db)


def unregister_player_from_tournament(user_email: str, tournament_id: int, db: Session):
    tournament = tournaments_crud.get_tournament_royale(tournament_id, db)
    if tournament.state != TournamentStates.REGISTRATION:
        raise WrongTournamentState()
    __remove_tournament_player(tournament_id, user_email, db)


def kick_player_from_tournament(team: str, tournament_id: int, db: Session):
    tournaments_crud.get_tournament_royale(tournament_id, db)
    user = get_user_by_team(team, db)
    tournaments_crud.remove_user_from_tournament_royale(user.id, tournament_id, db)


def register_in_tournament(user_email: str, tournament_id: int, db: Session):
    tournaments = tournaments_crud.get_tournament_royale(tournament_id, db)
    squad = get_user_squad_by_email(user_email, tournaments.game, db)
    players_count = reduce(lambda a, x: a + (x.replace(" ", "") != ''), squad.players, 0)
    if players_count < game_squad_sizes[tournaments.game.value]:
        raise NotEnoughPlayersInSquad()
    __add_user_to_tournament(tournament_id, user_email, db)


def update_tournament_stats(stats: Dict[str, List[int]], tournament_id: int, db: Session, commit=True):
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


def start_battleroyale_tournament(tournament_id: int):
    db = SessionLocal()
    debug_logger.info(f"started tournament {tournament_id}")
    tournament = tournaments_crud.get_tournament_royale(tournament_id, db)
    if len(tournament.users) < tournament.max_squads:
        pause_tournament(tournament_id, db)
        debug_logger.info(f"the number of registered players is less than required, the tournament {tournament_id} is paused")
        db.close()
        return
    tournaments_crud.update_tournament_state_royale(TournamentStates.IS_ON, tournament_id, db)
    create_empty_tournament_stats(tournament, db)
    db.close()


def end_battleroyale_tournament(tournament_id: int, db: Session):
    tournament = tournaments_crud.get_tournament_royale(tournament_id, db)
    if tournament.state != TournamentStates.IS_ON:
        raise TournamentAlreadyFinished(tournament_id)
    for stage in tournament.stages:
        if stage.state != StageStates.FINISHED:
            raise AllStagesMustBeFinished()
    tournaments_crud.update_tournament_state_royale(TournamentStates.FINISHED, tournament_id, db)
    for stats in tournament.stats:
        gl_stat_new = GlobalStatsEdit(score=stats.score, kills_count=stats.kills_count, wins_count=stats.wins_count)
        edit_global_stats(gl_stat_new, tournament.game, stats.user_id, db, False)
    db.commit()


def create_empty_tournament_stats(tournament, db):
    for user in tournament.users:
        stats = TournamentStats(
            game=tournament.game,
            user_id=user.id,
            tournament_id=tournament.id
        )
        db.add(stats)
    db.commit()


def match_players_stats(stats_list: List[MatchStats]) -> Dict[str, List[int]]:
    summary_score = {}
    for stats in stats_list:
        if stats.user.team_name in summary_score:
            summary_score[stats.user.team_name][0] += stats.score
            summary_score[stats.user.team_name][1] += stats.kills_count
            summary_score[stats.user.team_name][2] += stats.placement == 1
        else:
            summary_score[stats.user.team_name] = [stats.score, stats.kills_count, int(stats.placement == 1)]
    return summary_score


def end_stage(stage_id: int, db: Session):
    stage = get_stage_by_id(stage_id, db)
    tournament = db.query(Tournament).filter(Tournament.id == stage.tournament_id).first()
    if tournament.state != TournamentStates.IS_ON:
        raise WrongTournamentState()
    stage.state = StageStates.FINISHED
    db.add(stage)
    db.commit()
    stats = []
    for lobby in stage.lobbies:
        stats.extend(lobby.stats)
    stats_sum = match_players_stats(stats)
    update_tournament_stats(stats_sum, stage.tournament_id, db, True)
    stats_kills_sorted = sorted(stats_sum.items(), key=lambda x: x[1][1], reverse=True)
    range_min = min(3, len(stats_kills_sorted))
    leaders_for_save = StageLeadersEdit(kill_leaders=[])
    for i in range(range_min):
        leaders_for_save.kill_leaders.append(stats_kills_sorted[i][0])
    update_stage_leaders(leaders_for_save, stage_id, db)


def start_stage(stage_id: int, db: Session):
    stage = get_stage_by_id(stage_id, db)
    tournament = db.query(Tournament).filter(Tournament.id == stage.tournament_id).first()
    if tournament.state != TournamentStates.IS_ON:
        raise WrongTournamentState()
    if stage.state == StageStates.FINISHED:
        raise StageAlreadyFinished(stage.id)
    update_stage_state(stage_id, StageStates.IS_ON, db)


def save_row_stats(stats_schemas: List[MatchStatsCreate], lobby_id: int, db: Session):
    get_lobby(lobby_id, db)
    db.query(MatchStats).filter(MatchStats.lobby_id == lobby_id).delete()
    create_match_stats_list(stats_schemas, lobby_id, db)


def tournament_registrable_data(tournament_id: int, user_email: str, db: Session) -> Tuple[bool, bool]:
    tournament = tournaments_crud.get_tournament_royale(tournament_id, db)
    is_registered = tournaments_crud.is_user_in_tournament_royale(tournament.id, user_email, db)
    register_access = tournaments_crud.count_users_in_tournament_royale(tournament_id, db) < tournament.max_squads \
                      and tournament.state == TournamentStates.REGISTRATION
    return is_registered, register_access


def update_stage_leaders(leaders: StageLeadersEdit, stage_id: int, db: Session):
    stage = db.query(Stage).filter(Stage.id == stage_id).first()
    if leaders.kill_leaders is not None:
        stage.kill_leaders.clear()
        for leader in leaders.kill_leaders:
            user = get_user_by_team(leader, db)
            stage.kill_leaders.append(user)
    if leaders.damage_leaders is not None:
        stage.damage_leaders.clear()
        for leader in leaders.damage_leaders:
            user = get_user_by_team(leader, db)
            stage.damage_leaders.append(user)
    db.add(stage)
    db.commit()
