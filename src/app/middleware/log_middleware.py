from fastapi import Response, Request
from loguru import logger
from starlette.routing import Match

from src.app.database.db import SessionLocal


logger.add('access.log', format="{time} {level} {message}", level="INFO", rotation="1 week", compression='zip',
           filter=lambda record: record["extra"].get("name") == "access")
logger.add('error.log', format="{time} {level} {message}", level="ERROR", rotation="1 month", compression='zip',
           filter=lambda record: record["extra"].get("name") == "error")
error_logger = logger.bind(name="error")
access_logger = logger.bind(name="access")


class LoggingMiddleware:
    async def __call__(self, request: Request, call_next):
        try:
            request.state.db = SessionLocal()
            response = await call_next(request)
            access_logger.info(f"{request.method} {request.url}")
        except Exception as e:
            access_logger.error(f"{request.method} {request.url}")
            access_logger.debug(f"{request.method} {request.url}")
            routes = request.app.router.routes
            error_logger.debug("Params:")
            for route in routes:
                match, scope = route.matches(request)
                if match == Match.FULL:
                    for name, value in scope["path_params"].items():
                        error_logger.debug(f"\t{name}: {value}")
            error_logger.debug("Headers:")
            for name, value in request.headers.items():
                error_logger.debug(f"\t{name}: {value}")
            error_logger.error(str(e))
            raise e
        return response
