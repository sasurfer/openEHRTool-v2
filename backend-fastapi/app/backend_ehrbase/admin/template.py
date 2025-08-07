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
from lxml import etree


async def delete_templates_admin_ehrbase(
    request: Request, auth: str, url_base_admin: str
):
    logger = get_logger(request)
    logger.debug("inside delete_templates_admin_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        myurl = url_normalize(url_base_admin + "template/all")
        headers = {
            "Authorization": auth,
            "Content-Type": "application/json",
        }
        response = await fetch_delete_data(
            client=client, url=myurl, headers=headers, timeout=20000
        )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            myresp["templates"] = {"template": "All Templates deleted successfully"}
            myresp["templates"].update(json.loads(response.text))
        return myresp


async def delete_template_admin_ehrbase(
    request: Request,
    auth: str,
    url_base_admin: str,
    template_id: str,
):
    logger = get_logger(request)
    logger.debug("inside delete_template_admin_ehrbase")
    async with httpx.AsyncClient() as client:
        myurl = url_normalize(url_base_admin + "template/" + template_id)
        myresp = {}
        headers = {"Authorization": auth, "Content-Type": "application/json"}
        response = await fetch_delete_data(
            client=client, url=myurl, headers=headers, timeout=20000
        )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            myresp["template"] = {
                "template": f"Template {template_id} deleted successfully."
            }
            myresp["template"].update(json.loads(response.text))
        return myresp


async def put_template_admin_ehrbase(
    request: Request, auth: str, url_base_admin: str, template_id: str, template: str
):
    logger = get_logger(request)
    logger.debug("inside put_template_admin_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        headers = {
            "Authorization": auth,
            "Content-Type": "application/XML",
            "Accept": "application/XML",
        }
        params = {}
        myurl = url_normalize(url_base_admin + "template/" + template_id)
        response = await fetch_put_data(
            client=client,
            url=myurl,
            headers=headers,
            params=params,
            data=template,
            timeout=20000,
        )

        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
        return myresp
