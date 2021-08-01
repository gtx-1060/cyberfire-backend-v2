from sqlalchemy.orm import Session
from typing import List

from .tournaments import get_tournament, is_tournament_exists
from ..models.stage import Stage
from ..exceptions.base import ItemNotFound
from ..schemas.stage import StageCreate, StageEdit
from ..services.tournaments_service import set_tournament_dates


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
    # get_tournament(tournament_id, db)
    if not is_tournament_exists(tournament_id, db):
        raise ItemNotFound()
    for stage in stages:
        db_stage = Stage(
            title=stage.title,
            descriprion=stage.description,
            tournament_id=tournament_id,
            matches_count=stage.matches_count,
            stage_datetime=stage.stage_datetime
        )
        db.add(db_stage)
    db.commit()


def edit_stage(stage: StageEdit, stage_id: int, db: Session):
    db_stage = get_stage_by_id(stage_id, db)
    date_edit = False
    if stage.stage_datetime is not None:
        db_stage.stage_datetime = stage.stage_datetime
        date_edit = True
    if stage.title is not None:
        db_stage.title = stage.title
    if stage.description is not None:
        db_stage.description = stage.description
    if stage.damage_leaders is not None:
        db_stage.damage_leaders = stage.damage_leaders
    if stage.kill_leaders is not None:
        db_stage.kill_leaders = stage.kill_leaders
    if stage.keys is not None:
        db_stage.keys = stage.keys
    db.add(db_stage)
    db.commit()
    if date_edit:
        stages: List[StageCreate] = get_stages(db_stage.tournament_id, db)
        db_tournament = set_tournament_dates(stages, db_stage.tournament)
        db.add(db_tournament)
        db.commit()

