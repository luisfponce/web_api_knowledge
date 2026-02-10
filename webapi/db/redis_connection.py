from redis import Redis
from core import config

"""
docker run -d \
  --name redis-server \
  -p 6379:6379 \
  redis/redis-stack:latest
"""

def get_redis():
    redis = Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        password=config.REDIS_PSW,
        decode_responses=config.REDIS_DECODE_RESP
    )
    try:
        yield redis
    finally:
        redis.close()