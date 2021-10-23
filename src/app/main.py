from fastapi import FastAPI
import uvicorn
from loguru import logger
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from src.app.middleware.db_session_middleware import DatabaseSessionMiddleware
from src.app.config import STATIC_FILES_PATH
from src.app.middleware.log_middleware import LoggingMiddleware
from src.app.routers import news, users
from src.app.routers.royale import tournaments, lobbies, stats, stages
from src.app.routers.tvt import tournaments as tournaments_tvt, stats as stats_tvt
from src.app.routers.tvt.map_selector import websocket_lobby_selector
from src.app.services.dotenv_loader import env_vars
from src.app.services.schedule_service import myscheduler

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=env_vars["ALLOW_ORIGINS"].split(", "),
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
app.include_router(stats_tvt.router)
app.include_router(tournaments_tvt.router)
app.add_api_websocket_route('/api/v2/ws/lobby_selector', websocket_lobby_selector)


@app.on_event("startup")
async def startup_event():
    myscheduler.start()
    logger.info("server started")


@app.on_event("shutdown")
async def startup_event():
    myscheduler.stop()


def start():
    uvicorn.run("src.app.main:app", host="127.0.0.1", port=3020, log_level="critical")


if __name__ == "__main__":
    start()
