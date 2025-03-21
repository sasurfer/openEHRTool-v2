from fastapi import FastAPI, HTTPException, Depends,Request
from url_normalize import url_normalize
import httpx
from app.dependencies.redis_dependency import get_redis_client
from app.backend_redis.myredis import get_redis_status
import redis
from app.backend_ehrbase import fetch_get_data
from app.utils import get_logger



async def get_status(request: Request, auth : str,url_status: str):
    logger = get_logger(request)
    logger.debug('inside get_status') 
    async with httpx.AsyncClient() as client:
        # Retrieve data from EHRBase server
        status = []
        myurl = url_normalize(url_status)
        headers = {'Authorization': auth, 'Content-Type': 'application/json', 'Accept': 'application/json'}
        response=await fetch_get_data(client,myurl,headers)
        return response
