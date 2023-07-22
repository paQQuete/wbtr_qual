import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis import asyncio as aioredis

from api.v1 import auth
from core.config import SETTINGS
from core.logger import LOGGING
from db import redis_inj


redis_inj.redis_pool = aioredis.ConnectionPool(
    host=SETTINGS.REDIS.REDIS_HOST, port=SETTINGS.REDIS.REDIS_PORT, db=0, max_connections=200)


app = FastAPI(
    title=SETTINGS.PROJECT.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,

)

app.include_router(auth.router, prefix='/api/v1/auth', tags=['auth'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=9000,
        log_config=LOGGING,
        log_level=logging.DEBUG
    )
