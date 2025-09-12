from fastapi import FastAPI, HTTPException, Depends, Request
from url_normalize import url_normalize
import json
import httpx
from app.dependencies.redis_dependency import get_redis_client
from app.backend_redis.myredis import get_redis_status
import redis
from app.utils import get_logger, compareEhrbaseVersions
from app.backend_ehrbase import (
    fetch_get_data,
    fetch_post_data,
    fetch_put_data,
    fetch_delete_data,
)


async def put_contribution_admin_ehrbase(
    request: Request,
    auth: str,
    url_base_admin: str,
    contributionid: str,
    ehrid: str,
    contribution: str,
    format: str,
):
    logger = get_logger(request)
    logger.debug("inside put_contribution_admin_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        headers = {
            "Authorization": auth,
            "Prefer": "return=representation",
        }
        if format == "xml":
            headers["Content-Type"] = "application/xml"
            headers["Accept"] = "application/xml"
            params = {"format": "XML"}
        elif format == "json":
            headers["Content-Type"] = "application/json"
            headers["Accept"] = "application/json"
            params = {"format": "JSON"}
        else:
            logger.error(f"Invalid enum value: {format}")
            raise HTTPException(status_code=400, detail=f"Invalid enum value: {format}")
        params = {}
        myurl = url_normalize(
            url_base_admin + "ehr/" + ehrid + "/contribution/" + contributionid
        )
        response = await fetch_put_data(
            client=client,
            url=myurl,
            headers=headers,
            params=params,
            data=contribution,
            timeout=20000,
        )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
        return myresp
