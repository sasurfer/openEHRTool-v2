from fastapi import FastAPI, HTTPException, Depends, Request
from url_normalize import url_normalize
import json
import httpx
from app.backend_ehrbase import (
    fetch_get_data,
)
from lxml import etree
from app.utils import get_logger


async def get_status_admin_ehrbase(request: Request, auth: str, url_base_admin: str):
    logger = get_logger(request)
    logger.debug("inside get_status_admin_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        myurl = url_normalize(url_base_admin + "status")
        headers = {
            "Authorization": auth,
            "Content-Type": "application/json",
        }
        response = await fetch_get_data(
            client=client, url=myurl, headers=headers, timeout=20000
        )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            myresp["message"] = json.loads(response.text)
        return myresp
