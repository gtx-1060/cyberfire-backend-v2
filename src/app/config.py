from pathlib import Path
from os import getcwd
from os.path import join


AVATAR_PATH = ""
ABSOLUTE_PATH = getcwd()

# you need to make dir /static in the root folder and all included dirs (news, avatars, other) in it 

STATIC_FILES_PATH = join(Path(ABSOLUTE_PATH), "static")
NEWS_STATIC_PATH = join(STATIC_FILES_PATH, "news")
AVATARS_STATIC_PATH = join(STATIC_FILES_PATH, "avatars")
OTHER_STATIC_PATH = join(STATIC_FILES_PATH, "other")

USER = 'postgres'
PASSWORD = 'nba2003nba'
HOST = 'localhost'
DB = 'postgres'

SECRET_KEY = "91c37cdaacf6f6416b55a1714be4c039b050ff1536b52ab76bafca7b833aec93"
ALGORITHM = "HS256"
ACCESS_ALLOWED_ADDRESSES = '*'
REFRESH_TOKEN_EXPIRE_DAYS = 20
