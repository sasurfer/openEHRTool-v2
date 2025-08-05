from fastapi import APIRouter, HTTPException, Request, Depends, Query
from app.security import verify_jwt_token, get_token_from_header
from uuid import UUID
from app.utils import get_logger
from fastapi.responses import JSONResponse

from app.utils import (
    filter_methods,
    filter_type,
    filter_outcome,
    filter_order,
    filter_customsearch,
)
import redis
from app.dependencies.redis_dependency import get_redis_client
from typing import Optional
import json

router = APIRouter()


@router.get("/")
async def get_log(
    request: Request,
    methodType: str = Query(...),
    onwhat: str = Query(...),
    outcome: str = Query(...),
    order: str = Query(...),
    customsearch: str = Query(""),
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside get_log")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        dvalues = redis_client.lrange("log", 0, -1)
        if not dvalues:
            return JSONResponse(content={"log": []}, status_code=200)
        results = filter_methods(dvalues, methodType)
        logger.debug(f"results after filter_methods: {results}")
        if not results:
            return JSONResponse(content={"log": []}, status_code=200)
        results = filter_type(results, onwhat)
        logger.debug(f"results after filter_type: {results}")
        if not results:
            return JSONResponse(content={"log": []}, status_code=200)
        results = filter_outcome(results, outcome)
        logger.debug(f"results after filter_outcome: {results}")
        if not results:
            return JSONResponse(content={"log": []}, status_code=200)
        results = filter_order(results, order)
        logger.debug(f"results after filter_order: {results}")
        if not results:
            return JSONResponse(content={"log": []}, status_code=200)
        results = filter_customsearch(results, customsearch)
        logger.debug(f"results after filter_customsearch: {results}")
        if not results:
            return JSONResponse(content={"log": []}, status_code=200)
        return JSONResponse(content={"log": results}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during get_log: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.delete("/")
async def delete_log(
    request: Request,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside delete_log")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        logger.debug("before")
        redis_client.delete("log")
        if not redis_client.exists("log"):
            return JSONResponse(content={"log": "Redis log deleted"}, status_code=200)
        else:
            return JSONResponse(
                content={"Error": "Failed to delete Redis log"}, status_code=500
            )
    except Exception as e:
        logger.error(f"An exception occurred during delete_log: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
