from contextlib import asynccontextmanager
from typing import Optional
from urllib.parse import urlparse
import redis.asyncio as redis

class RedisManager:
    """
    A class that manages Redis operations with an async client.
    """
    def __init__(self, redis_url: str):
        parsed_url = urlparse(redis_url)
        self.redis_host = parsed_url.hostname
        self.redis_port = parsed_url.port
        self.redis_db = int(parsed_url.path.strip("/")) if parsed_url.path.strip("/") else 0

        self.client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            db=self.redis_db,
            decode_responses=True
        )

    @asynccontextmanager
    async def connect(self):
        """
        Provides an async Redis client via a context manager.
        """
        try:
            yield self.client
        finally:
            await self.client.close()

    async def increment_request_count(self, user_id: str, org_id: Optional[str], rule_id: str, expiration: int = 3600) -> list:
        async with self.connect() as client:
            key = f"user:{user_id}:org:{org_id}:rule:{rule_id}"
            is_new = await client.setnx(key, 0)
            count = await client.incr(key)

            if is_new:
                await client.expire(key, expiration)

        return [True, {"key": key, "count": count}, "SUCCESS"]

    async def get_request_count(self, user_id: str, org_id: Optional[str], rule_id: str) -> int:
        async with self.connect() as client:
            key = f"user:{user_id}:org:{org_id}:rule:{rule_id}"
        return int(await client.get(key) or 0)

    async def reset_request_count(self, user_id: str, org_id: Optional[str], rule_id: str):
        async with self.connect() as client:
            key = f"user:{user_id}:org:{org_id}:rule:{rule_id}"
            await client.delete(key)
