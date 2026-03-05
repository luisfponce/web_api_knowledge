from redis import Redis

from core import config


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