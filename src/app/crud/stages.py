from sqlalchemy.orm import Session
from typing import List

from .tournaments import is_tournament_exists
from ..models.stage import Stage
from ..exceptions.base import ItemNotFound
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
        raise ItemNotFound()
    return stage


def create_stages(stages: List[StageCreate], tournament_id: int, db: Session):
    if not is_tournament_exists(tournament_id, db):
        raise ItemNotFound()
    for stage in stages:
        db_stage = Stage(
            title=stage.title,
            description=stage.description,
            tournament_id=tournament_id,
            stage_datetime=stage.stage_datetime,
            lobbies_count=len(stage.lobbies)
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
    if stage.damage_leaders is not None:
        db_stage.damage_leaders = stage.damage_leaders
    if stage.kill_leaders is not None:
        db_stage.kill_leaders = stage.kill_leaders
    if stage.lobbies_count is not None:
        db_stage.lobbies_count = stage.lobbies_count
    db.add(db_stage)
    db.commit()


def update_stage_state(stage_id: int, state: StageStates, db: Session):
    db.query(Stage).filter(Stage.id == stage_id).update({
        state: state
    })
    db.commit()
