from fastapi import Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
import redis

def get_redis_client(request: Request) -> redis.StrictRedis:
    redis_client = request.app.state.redis_client
    if redis_client is None:
        raise HTTPException(status_code=500, detail="Redis client is not available")
    return redis_client