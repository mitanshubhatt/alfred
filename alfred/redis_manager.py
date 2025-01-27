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

    async def increment_request_count(self, user_id: int, org_id: int, rule_id: str, expiration: int = 3600) -> int:
        key = f"user:{user_id}:org:{org_id}:rule:{rule_id}"
        is_new = await self.client.setnx(key, 0)
        count = await self.client.incr(key)

        if is_new:
            await self.client.expire(key, expiration)

        return count

    async def get_request_count(self, user_id: int, org_id: int, rule_id: str) -> int:
        key = f"user:{user_id}:org:{org_id}:rule:{rule_id}"
        return int(await self.client.get(key) or 0)

    async def reset_request_count(self, user_id: int, org_id: int, rule_id: str):
        key = f"user:{user_id}:org:{org_id}:rule:{rule_id}"
        await self.client.delete(key)
