from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.app.services.dotenv_loader import env_vars

SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg2://{env_vars["DB_USER"]}:{env_vars["DB_PASSWORD"]}@{env_vars["DB_HOST"]}/{env_vars["DB_NAME"]}'

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
