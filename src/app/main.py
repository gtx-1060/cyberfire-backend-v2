from fastapi import FastAPI
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from src.app.middleware.db_session_middleware import DatabaseSessionMiddleware
from src.app.config import STATIC_FILES_PATH
from src.app.routers import news, users, stats

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost', "http://127.0.0.1:3005"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.middleware("http")(DatabaseSessionMiddleware())

app.mount("/static", StaticFiles(directory=STATIC_FILES_PATH), name="static")
app.include_router(news.router)
app.include_router(users.router)
app.include_router(stats.router)


def start():
    uvicorn.run("src.app.main:app", host="127.0.0.1", port=3001)


if __name__ == "__main__":
    start()
