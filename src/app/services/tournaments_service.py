from datetime import datetime
from typing import List

from src.app.models.tournament import Tournament
from src.app.schemas.stage import StageCreate


def set_tournament_dates(stages: List[StageCreate], tournament: Tournament) -> Tournament:
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

