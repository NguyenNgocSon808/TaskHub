from redis import asyncio as aioredis
from app.core.config import settings

# Tạo connection pool tới Redis
redis_client = aioredis.from_url(
    settings.REDIS_URL, 
    encoding="utf-8", 
    decode_responses=True
)
