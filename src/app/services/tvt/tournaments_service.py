from datetime import datetime, timedelta
from functools import reduce
from typing import Tuple
import pytz
from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.app.crud.tvt import tournaments as tournaments_crud
from src.app.crud.user import get_user_squad_by_email, get_user_by_email, get_user_by_team
from src.app.database.db import SessionLocal
from src.app.exceptions.tournament_exceptions import *
from src.app.schemas.tvt import matches as match_schemas, stages as stage_schemas
from src.app.models.games import game_squad_sizes
from src.app.models.tournament_events import TournamentEvents
from src.app.models.tournament_states import TournamentStates
from src.app.models.tvt.match import TvtMatch
from src.app.models.tvt.stage import TvtStage
from src.app.models.tvt.team_stats import TvtStats
from src.app.models.tvt.tournament import TvtTournament
from src.app.models.user import User
from src.app.schemas.tvt.tournaments import TvtTournamentCreate
from src.app.services.schedule_service import myscheduler
from src.app.services.redis_service import redis_client


TIME_TO_CONNECT_AT_LAUNCH = timedelta(minutes=5)


def get_tournament_task_id(event: TournamentEvents, tournament_id: int):
    return f"{event.value}_{tournament_id}"


def tournament_registrable_data_tvt(tournament_id: int, user_email: str, db: Session) -> Tuple[bool, bool]:
    tournament = tournaments_crud.get_tournament_tvt(tournament_id, db)
    is_registered = tournaments_crud.is_user_in_tournament_tvt(tournament.id, user_email, db)
    register_access = tournaments_crud.count_users_in_tournament_tvt(tournament_id, db) < tournament.max_squads \
                      and tournament.state == TournamentStates.REGISTRATION
    return is_registered, register_access


def schedule_tournament(db_tournament, db: Session, autoremove=True):
    try:
        remove_tournament_tvt_jobs(db_tournament.id)
        myscheduler.plan_task(get_tournament_task_id(TournamentEvents.START_TOURNAMENT_TVT, db_tournament.id),
                              db_tournament.start_date, start_tvt_tournament, [db_tournament.id])
    except Exception as e:
        if autoremove:
            tournaments_crud.remove_tournament_tvt(db_tournament.id, db)
        raise e


def remove_tournament_tvt_jobs(tournament_id):
    tstart_task_id = get_tournament_task_id(TournamentEvents.START_TOURNAMENT_TVT, tournament_id)
    if myscheduler.task_exists(tstart_task_id):
        myscheduler.remove_task(tstart_task_id)


def create_tournament_tvt(tournament_create: TvtTournamentCreate, db: Session) -> dict:
    now_moscow = datetime.now(pytz.timezone('Europe/Moscow'))
    if tournament_create.start_date.timestamp() < now_moscow.timestamp():
        raise WrongTournamentDates(tournament_create.start_date)
    db_tournament = tournaments_crud.create_tournament_tvt(tournament_create, db)
    create_stage(0, db_tournament.id, db)
    schedule_tournament(db_tournament, db)
    return {"tournament_id": db_tournament.id}


def create_stage(index: int, tournament_id: int, db):
    stage = TvtStage(tournament_id=tournament_id, index=index)
    db.add(stage)
    db.commit()


def start_tvt_tournament(tournament_id: int):
    db = SessionLocal()
    tournament = tournaments_crud.get_tournament_tvt(tournament_id, db)
    tournaments_crud.update_tournament_state_tvt(TournamentStates.IS_ON, tournament_id, db)
    launch_at = datetime.now()+TIME_TO_CONNECT_AT_LAUNCH
    redis_client.add_val(f'tournament_launch:{tournament_id}', launch_at.isoformat(), TIME_TO_CONNECT_AT_LAUNCH)
    redis_client.remove(f'tournament_launch:{tournament_id}:users')
    myscheduler.plan_task(get_tournament_task_id(TournamentEvents.START_TEAMS_MANAGEMENT, tournament_id),
                          launch_at+timedelta(seconds=10), start_admin_management_state, [tournament_id], 60)
    db.close()


def add_to_wait_room(email: str, tournament_id: int):
    key = f'tournament_launch:{tournament_id}:users'
    ex = redis_client.exists(key)
    redis_client.add_to_set(key, email)
    if not ex:
        redis_client.client.expire(key, timedelta(minutes=30))


def remove_from_wait_room(email: str, tournament_id: int):
    redis_client.remove_from_set(f'tournament_launch:{tournament_id}:users', email)


def start_admin_management_state(tournament_id: int):
    # TODO: STAGE STATE CHANGE NEEDED
    db: Session = SessionLocal()
    db_stage = tournaments_crud.get_last_tournament_stage(tournament_id, db)
    emails = redis_client.get_set(f'tournament_launch:{tournament_id}:users')
    stage = stage_schemas.TvtStage.from_orm(db_stage)
    teams_active = set()
    for email in emails:
        teams_active.add(get_user_by_email(email, db).team_name)

    matches_to_remove = []
    for i in range(len(stage.matches)):
        match = stage.matches[i]
        removed = 0
        for stats in match.teams_stats:
            if stats.user.team_name not in teams_active:
                stats.user.team_name = None
                removed += 1
        if removed == 2:
            matches_to_remove.append(i)
    for ind in matches_to_remove:
        stage.matches.pop(ind)
    redis_client.add_val(f'tournament:{tournament_id}:temp_stage', stage.json(), expire=timedelta(minutes=20))


def to_next_stage(team: str, tournament_id: int, db: Session):
    pass


def save_scoreboard(db: Session):
    pass


def register_in_tournament(user_email: str, tournament_id: int, db: Session):
    tournament = tournaments_crud.get_tournament_tvt(tournament_id, db)
    user = get_user_by_email(user_email, db)
    verify_squad(tournament, user_email, db)
    __add_user_to_tournament(tournament_id, user, db)
    __append_in_match(tournament, user, db)


def __append_in_match(tournament: TvtTournament, user: User, db):
    fstage: TvtStage = tournament.stages[0]
    saved = False
    for match in fstage.matches:
        if len(match.teams_stats) == 1:
            ar_id = match.teams_stats[0].user_id
            new_stats = TvtStats(
                score=0,
                user_id=user.id,
                arrival_id=ar_id,
                match_id=match.id,
                tournament_id=tournament.id
            )
            match.teams_stats.append(new_stats)
            match.teams_stats[0].arrival_id = new_stats.user_id
            db.add(match)
            saved = True
            break
    if not saved:
        ind = 0 if len(fstage.matches) == 0 else fstage.matches[-1].index + 1
        new_match = TvtMatch(
            stage_id=fstage.id,
            index=ind
        )
        db.add(new_match)
        db.commit()
        db.refresh(new_match)
        new_stats = TvtStats(
            score=0,
            user_id=user.id,
            arrival_id=None,
            match_id=new_match.id,
            tournament_id=tournament.id
        )
        new_match.teams_stats.append(new_stats)
        db.add(new_match)
    db.commit()


def verify_squad(tournament: TvtTournament, user_email: str, db):
    squad = get_user_squad_by_email(user_email, tournament.game, db)
    players_count = reduce(lambda a, x: a + (x.replace(" ", "") != ''), squad.players, 0)
    if players_count < game_squad_sizes[tournament.game.value]:
        raise NotEnoughPlayersInSquad()


def kick_player_from_tournament(team_name: str, tournament_id: int, db: Session):
    user = get_user_by_team(team_name, db)
    tournaments_crud.get_tournament_tvt(tournament_id, db)
    tournaments_crud.remove_user_from_tournament_tvt(user.id, tournament_id, db)
    __remove_from_last_match(tournament_id, user, db)


def unregister_player_from_tournament(user_email: str, tournament_id: int, db: Session):
    tournament = tournaments_crud.get_tournament_tvt(tournament_id, db)
    if tournament.state != TournamentStates.REGISTRATION:
        raise WrongTournamentState()
    user = get_user_by_email(user_email, db)
    tournaments_crud.remove_user_from_tournament_tvt(user.id, tournament_id, db)
    __remove_from_last_match(tournament_id, user, db)


def __remove_from_last_match(tournament_id, user, db):
    stats = db.query(TvtStats)\
        .filter(and_(TvtStats.user_id == user.id, TvtStats.tournament_id == tournament_id))\
        .order_by(TvtStats.id.desc()).first()
    if stats.arrival_id is not None:
        ar_stats: TvtStats = db.query(TvtStats)\
            .filter(and_(TvtStats.user_id == stats.arrival_id, TvtStats.tournament_id == tournament_id))\
            .order_by(TvtStats.id.desc()).first()
        ar_stats.arrival_id = None
        db.add(ar_stats)
        db.query(TvtStats).filter(TvtStats.id == stats.id).delete()
    else:
        db.query(TvtMatch).filter(TvtMatch.id == stats.match_id).delete()
    db.commit()


def __add_user_to_tournament(tournament_id: int, user: User, db: Session):
    tournament = tournaments_crud.get_tournament_tvt(tournament_id, db)
    if tournament.state != TournamentStates.REGISTRATION:
        raise WrongTournamentState()
    if user in tournament.users:
        raise UserAlreadyRegistered(user.email)
    if len(tournament.users) < tournament.max_squads:
        tournament.users.append(user)
    else:
        raise MaxSquadsCount()
    db.add(tournament)
    db.commit()
