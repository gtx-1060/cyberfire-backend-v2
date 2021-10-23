from pathlib import Path
from os import getcwd
from os.path import join

ABSOLUTE_PATH = getcwd()

# you need to make dir /static in the root folder and all included dirs (news, avatars, other) in it 

STATIC_FILES_PATH = join(Path(ABSOLUTE_PATH), "static")
NEWS_STATIC_PATH = join(STATIC_FILES_PATH, "news")
AVATARS_STATIC_PATH = join(STATIC_FILES_PATH, "avatars")
OTHER_STATIC_PATH = join(STATIC_FILES_PATH, "other")
PROOFS_STATIC_PATH = join(STATIC_FILES_PATH, "proofs")

DEFAULT_AVATAR_PATH = "static/avatars/default.jpg"
DEFAULT_IMAGE_PATH = "static/news/default.jpg"
DEFAULT_PROOF_PATH = "static/proofs/default.jpg"
DEFAULT_VERIFIED_PATH = "static/proofs/verified.jpg"


ALGORITHM = "HS256"
REFRESH_TOKEN_EXPIRE_DAYS = 20
