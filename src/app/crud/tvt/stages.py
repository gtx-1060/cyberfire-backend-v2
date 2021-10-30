from typing import List
from sqlalchemy.orm import Session

from src.app.exceptions.base import ItemNotFound
from src.app.models.tournament_states import StageStates
from src.app.models.tvt.match import TvtMatch
from src.app.models.tvt.stage import TvtStage as Stage, TvtStage, suspended_association_table


def get_stages(tournament_id: int, db: Session) -> List[Stage]:
    stages = db.query(Stage).filter(Stage.tournament_id == tournament_id).all()
    if stages is None:
        return []
    return stages


def get_stage_by_id(stage_id: int, db: Session) -> Stage:
    stage = db.query(Stage).filter(Stage.id == stage_id).first()
    if stage is None:
        raise ItemNotFound(Stage)
    return stage


def create_stage(index: int, tournament_id: int, db):
    stage = TvtStage(tournament_id=tournament_id, index=index)
    db.add(stage)
    db.commit()
    db.refresh(stage)
    return stage


def create_match(stage_id: int, index: int, db: Session):
    new_match = TvtMatch(
        stage_id=stage_id,
        index=index
    )
    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    return new_match


def update_stage_state(stage_id: int, state: StageStates, db: Session):
    db.query(Stage).filter(Stage.id == stage_id).update({
        Stage.state: state
    })
    db.commit()


def clear_absent_users(stage_id: int, db: Session):
    db.query(suspended_association_table).filter(suspended_association_table.c.stage_id == stage_id).delete()
    db.commit()
