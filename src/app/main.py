from fastapi import FastAPI
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from src.app.middleware.db_session_middleware import DatabaseSessionMiddleware
from src.app.config import STATIC_FILES_PATH
from src.app.middleware.log_middleware import LoggingMiddleware
from src.app.routers import news, users
from src.app.routers.royale import tournaments, lobbies, stats, stages
from src.app.routers.tvt import tournaments as tournaments_tvt
from src.app.services.schedule_service import myscheduler

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost', "http://127.0.0.1:3005"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.middleware("http")(LoggingMiddleware())
app.middleware("http")(DatabaseSessionMiddleware())

app.mount("/api/v2/static", StaticFiles(directory=STATIC_FILES_PATH), name="static")
app.include_router(news.router)
app.include_router(users.router)
app.include_router(stats.router)
app.include_router(stages.router)
app.include_router(tournaments.router)
app.include_router(lobbies.router)
app.include_router(tournaments_tvt.router)


@app.on_event("startup")
async def startup_event():
    myscheduler.start()


@app.on_event("shutdown")
async def startup_event():
    myscheduler.stop()


def start():
    uvicorn.run("src.app.main:app", host="127.0.0.1", port=3020)


if __name__ == "__main__":
    start()
