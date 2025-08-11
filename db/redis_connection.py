import os
from redis import Redis

"""
docker run -d \
  --name redis-server \
  -p 6379:6379 \
  redis/redis-stack:latest
"""

def get_redis():
    redis = Redis(
        host="127.0.0.1",
        port=6379,
        password=None,
        decode_responses=True
    )
    try:
        yield redis
    finally:
        redis.close()