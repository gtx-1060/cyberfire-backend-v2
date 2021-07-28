from fastapi import Response, Request
from src.app.database.db import SessionLocal


class DatabaseSessionMiddleware:
    async def __call__(self, request: Request, call_next):
        response = Response("Internal server error", status_code=500)
        try:
            request.state.db = SessionLocal()
            response = await call_next(request)
        finally:
            request.state.db.close()
        return response
