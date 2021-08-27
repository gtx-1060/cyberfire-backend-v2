from sqlalchemy import create_engine

from .db import SQLALCHEMY_DATABASE_URL
from src.app.models.user import User
from src.app.models.royale.squad import Squad
from src.app.models.news import News
from src.app.models.royale.stage import Stage, damagers_association_table, kills_association_table
from src.app.models.royale.tournament import Tournament, association_table
from src.app.models.royale.stats import MatchStats, TournamentStats, GlobalStats
from src.app.models.royale.lobbies import Lobby
from src.app.models.tvt.tournament import TvtTournament
from src.app.models.tvt.stage import TvtStage
from src.app.models.tvt.match import TvtMatch
from src.app.models.tvt.team_stats import TvtStats
from .db import Base

# my_tables = [User.__table__, Squad.__table__, News.__table__, Stage.__table__, Lobby.__table__, Tournament.__table__,
#              MatchStats.__table__, TournamentStats.__table__, GlobalStats.__table__, association_table,
#              kills_association_table, damagers_association_table]


def create_tables():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_recycle=3600)
    Base.metadata.create_all(engine)


def run_drop_tables():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_recycle=3600)
    Base.metadata.drop_all(engine)

