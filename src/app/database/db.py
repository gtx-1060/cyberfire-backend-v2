from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

USER = ''
PASSWORD = ''
HOST = ''
DB = ''

SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}/{DB}'

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
