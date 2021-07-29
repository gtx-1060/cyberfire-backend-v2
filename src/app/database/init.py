from sqlalchemy import create_engine

from .db import Base
from .db import SQLALCHEMY_DATABASE_URL
from src.app.models.user import User
from src.app.models.squad import Squad
from src.app.models.news import News
from src.app.models.stage import Stage
from src.app.models.tournament import Tournament
from src.app.models.stats import MatchStats, TournamentStats, GlobalStats

my_tables = [User.__table__, Squad.__table__, News.__table__, Stage.__table__, Tournament.__table__,
             MatchStats.__table__, TournamentStats.__table__, GlobalStats.__table__]


def create_tables():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_recycle=3600)
    Base.metadata.create_all(engine, tables=my_tables)


def run_drop_tables():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_recycle=3600)
    Base.metadata.drop_all(engine, tables=my_tables)

