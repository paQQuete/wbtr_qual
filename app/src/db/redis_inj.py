from typing import Optional

from redis import asyncio as aioredis
from redis.asyncio import Redis, ConnectionPool

redis_pool: Optional[ConnectionPool] = None


async def get_redis() -> Redis:
    return aioredis.Redis(connection_pool=redis_pool)
