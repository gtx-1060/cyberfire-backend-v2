from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

USER = 'postgres'
PASSWORD = 'nba2003nba'
HOST = 'localhost'
DB = 'postgres'

SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}/{DB}'

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
