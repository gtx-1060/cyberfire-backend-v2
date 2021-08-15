import logging

from fastapi import FastAPI
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from src.app.middleware.db_session_middleware import DatabaseSessionMiddleware
from src.app.config import STATIC_FILES_PATH
from src.app.routers import news, users, stats, stages, tournaments, lobbies
from src.app.services.schedule_service import myscheduler

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost', "http://127.0.0.1:3005"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
# app.middleware("http")(LoggingMiddleware())
app.middleware("http")(DatabaseSessionMiddleware())

app.mount("/api/v2/static", StaticFiles(directory=STATIC_FILES_PATH), name="static")
app.include_router(news.router)
app.include_router(users.router)
app.include_router(stats.router)
app.include_router(stages.router)
app.include_router(tournaments.router)
app.include_router(lobbies.router)


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
