from fastapi import FastAPI, HTTPException, Depends, Request
from url_normalize import url_normalize
import json
import httpx
from app.dependencies.redis_dependency import get_redis_client
from app.backend_redis.myredis import get_redis_status
import redis
from app.utils import get_logger
from app.backend_ehrbase import (
    fetch_get_data,
    fetch_post_data,
    fetch_put_data,
    fetch_delete_data,
)
from lxml import etree
from app.utils import get_logger, compareEhrbaseVersions, composition_check
from fastapi import HTTPException, Request
from app.backend_ehrbase.ehr.ehr import (
    get_ehr_by_ehrid_ehrbase,
    post_ehr_by_ehrid_ehrbase,
)
from app.backend_ehrbase.sidebar.rsidebar.rsidebar import get_sidebar_ehrs_ehrbase


async def post_contribution_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    ehrid: str,
    contribution: str,
    format: str,
):
    logger = get_logger(request)
    logger.debug("inside post_contribution_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        headers = {
            "Authorization": auth,
            "Prefer": "return=representation",
        }
        myurl = url_normalize(url_base + "ehr/" + ehrid + "/contribution")
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
        response = await fetch_post_data(
            client=client,
            url=myurl,
            headers=headers,
            data=contribution,
            params=params,
            timeout=20000,
        )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            myresp["contributionid"] = response.headers["Location"].split(
                "contribution/"
            )[1]
            myresp["contribution"] = {
                "status": myresp["status"],
                "contributionid": myresp["contributionid"],
            }
        return myresp


async def get_contribution_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    contributionid: str,
    ehrid: str,
    format: str,
):
    logger = get_logger(request)
    logger.debug("inside get_contribution_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        headers = {
            "Authorization": auth,
            "Prefer": "return=representation",
        }
        myurl = url_normalize(
            url_base + "ehr/" + ehrid + "/contribution/" + contributionid
        )
        if format == "xml":
            headers["Accept"] = "application/xml"
            headers["Content-Type"] = "application/xml"
            params = {"format": "XML"}
        elif format == "json":
            headers["Accept"] = "application/json"
            headers["Content-Type"] = "application/json"
            params = {"format": "JSON"}
        else:
            logger.error(f"Invalid enum value: {format}")
            raise HTTPException(status_code=400, detail=f"Invalid enum value: {format}")
        response = await fetch_get_data(
            client=client,
            url=myurl,
            headers=headers,
            params=params,
            timeout=20000,
        )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            contribution = ""
            if format == "xml":
                root = etree.fromstring(response.text)
                contribution = etree.tostring(
                    root, encoding="unicode", method="xml", pretty_print=True
                )
            elif format == "json":
                contribution = json.loads(response.text)
            else:
                logger.error(f"Invalid enum value: {format}")
                raise HTTPException(
                    status_code=400, detail=f"Invalid enum value: {format}"
                )

            myresp["contribution"] = contribution
        return myresp
