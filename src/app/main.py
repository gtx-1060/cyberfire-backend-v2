from fastapi import FastAPI
import uvicorn
from starlette.middleware.cors import CORSMiddleware

from middleware.db_session_middleware import DatabaseSessionMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['https://localhost', "https://localhost:3005"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.middleware("http")(DatabaseSessionMiddleware())

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=3001)


