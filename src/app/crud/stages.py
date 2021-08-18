from sqlalchemy.orm import Session
from typing import List

from .tournaments import is_tournament_exists
from ..models.stage import Stage, kills_association_table, damagers_association_table
from ..exceptions.base import ItemNotFound
from ..models.tournament import Tournament
from ..models.tournament_states import StageStates
from ..schemas.stage import StageCreate, StageEdit


def get_stages(tournament_id: int, db: Session) -> List[Stage]:
    stages = db.query(Stage).filter(Stage.tournament_id == tournament_id).order_by(Stage.stage_datetime).all()
    if stages is None:
        return []
    return stages


def get_stage_by_id(stage_id: int, db: Session) -> Stage:
    stage = db.query(Stage).filter(Stage.id == stage_id).first()
    if stage is None:
        raise ItemNotFound(Stage)
    return stage


def create_stages(stages: List[StageCreate], tournament_id: int, db: Session):
    if not is_tournament_exists(tournament_id, db):
        raise ItemNotFound(Tournament)
    for stage in stages:
        db_stage = Stage(
            title=stage.title,
            description=stage.description,
            tournament_id=tournament_id,
            stage_datetime=stage.stage_datetime,
        )
        db.add(db_stage)
    db.commit()


def edit_stage(stage: StageEdit, stage_id: int, db: Session):
    db_stage = get_stage_by_id(stage_id, db)
    if stage.stage_datetime is not None:
        db_stage.stage_datetime = stage.stage_datetime
    if stage.title is not None:
        db_stage.title = stage.title
    if stage.description is not None:
        db_stage.description = stage.description
    db.add(db_stage)
    db.commit()


def update_stage_state(stage_id: int, state: StageStates, db: Session):
    db.query(Stage).filter(Stage.id == stage_id).update({
        state: state
    })
    db.commit()


def remove_user_from_stages_leaders(user_id: int, db: Session):
    db.query(kills_association_table).filter(kills_association_table.c.users_id == user_id).delete()
    db.query(damagers_association_table).filter(damagers_association_table.c.users_id == user_id).delete()
    db.commit()
