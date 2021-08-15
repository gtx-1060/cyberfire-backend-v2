from fastapi import Request
from loguru import logger
from starlette.routing import Match

from src.app.database.db import SessionLocal

# DEBUG LOG FLAG CONSTANT
DEBUG = False
needed_headers = {'authorization', 'host', 'content-type'}

logger.add('access.log', format="{time} {level} {message}", level="INFO", rotation="1 week", compression='zip',
           filter=lambda record: record["extra"].get("name") == "access")
logger.add('debug.log', format="{time} {level} {message}", level="TRACE", rotation="1 week", compression='zip',
           filter=lambda record: record["extra"].get("name") == "debug")
logger.add('error.log', format="{time} {level} {message}", level="ERROR", rotation="1 month", compression='zip',
           filter=lambda record: record["extra"].get("name") == "error")
error_logger = logger.bind(name="error")
access_logger = logger.bind(name="access")
debug_logger = logger.bind(name="debug")


class LoggingMiddleware:
    async def __call__(self, request: Request, call_next):
        try:
            request.state.db = SessionLocal()
            if DEBUG:
                await LoggingMiddleware.log_all(debug_logger, request)
            response = await call_next(request)
            access_logger.info(f"{request.method} {request.url}")
        except Exception as e:
            access_logger.error(f"{request.method} {request.url}")
            await LoggingMiddleware.log_all(error_logger, request)
            error_logger.error(str(e))
            raise e
        return response

    @staticmethod
    async def log_all(mlogger, request):
        mlogger.info(f"{request.method} {request.url}")
        routes = request.app.router.routes
        mlogger.debug("Params:")
        for route in routes:
            match, scope = route.matches(request)
            if match == Match.FULL:
                for name, value in scope["path_params"].items():
                    mlogger.debug(f"\t{name}: {value}")
        mlogger.debug("Headers:")
        for name, value in request.headers.items():
            if name.lower() in needed_headers:
                mlogger.debug(f"\t{name}: {value}")
