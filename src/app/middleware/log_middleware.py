from fastapi import Response, Request
from loguru import logger
from starlette.routing import Match

from src.app.database.db import SessionLocal


logger.add('access.log', format="{time} {level} {message}", level="ACCESS", rotation="1 week", compression='zip')
logger.add('error.log', format="{time} {level} {message}", level="ERROR", rotation="1 month", compression='zip')


class LoggingMiddleware:
    async def __call__(self, request: Request, call_next):
        logger.info(f"{request.method} {request.url}")
        try:
            request.state.db = SessionLocal()
            response = await call_next(request)

        except Exception as e:
            logger.error(str(e))
            routes = request.app.router.routes
            logger.debug("Params:")
            for route in routes:
                match, scope = route.matches(request)
                if match == Match.FULL:
                    for name, value in scope["path_params"].items():
                        logger.debug(f"\t{name}: {value}")
            logger.debug("Headers:")
            for name, value in request.headers.items():
                logger.debug(f"\t{name}: {value}")
            raise e
        return response
