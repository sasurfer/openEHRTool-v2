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


async def get_templates_ehrbase(request: Request, auth: str, url_base: str):
    logger = get_logger(request)
    logger.debug("inside get_templates_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        params = {format: "json"}
        myurl = url_normalize(url_base + "definition/template/adl1.4")
        headers = {
            "Authorization": auth,
            "Content-Type": "application/json",
        }
        response = await fetch_get_data(
            client=client, url=myurl, headers=headers, timeout=20000, params=params
        )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            myresp["template"] = json.loads(response.text)
        return myresp


async def get_template_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    url_base_ecis: str,
    template_id: str,
    format: str,
    ehrbase_version: str,
):
    logger = get_logger(request)
    logger.debug("inside get_template_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        params = {"format": "JSON"}
        if format == "opt":
            myurl = url_normalize(
                url_base + "definition/template/adl1.4/" + template_id
            )
            headers = {"Authorization": auth, "Content-Type": "application/xml"}
            response = await fetch_get_data(
                client=client, url=myurl, headers=headers, timeout=20000, params=params
            )
            response.raise_for_status()
            myresp["status_code"] = response.status_code
            if 200 <= response.status_code < 210:
                myresp["status"] = "success"
                root = etree.fromstring(response.text)
                responsexml = etree.tostring(
                    root, encoding="unicode", method="xml", pretty_print=True
                )
                responsexml = responsexml.replace("#", "%23")
                myresp["template"] = responsexml
            return myresp
        else:  # format webtemplate
            if compareEhrbaseVersions(ehrbase_version, "2.5.0") > 0:
                myurl = url_normalize(
                    url_base + "definition/template/adl1.4/" + template_id
                )
                headers = {
                    "Authorization": auth,
                    "Content-Type": "application/JSON",
                    "Accept": "application/openehr.wt+json",
                }
                response = await fetch_get_data(
                    client=client,
                    url=myurl,
                    headers=headers,
                    timeout=20000,
                    params=params,
                )
                response.raise_for_status()
            else:  # EHRBase version<2.5.0
                myurl = url_normalize(url_base_ecis + "template/" + template_id)
                headers = {
                    "Authorization": auth,
                    "Content-Type": "application/openehr.wt+json",
                }
                response = await fetch_get_data(
                    client=client,
                    url=myurl,
                    headers=headers,
                    timeout=20000,
                    params=params,
                )
                response.raise_for_status()
            myresp["status_code"] = response.status_code
            if 200 <= response.status_code < 210:
                myresp["status"] = "success"
                myresp["template"] = json.loads(response.text)
            return myresp


async def post_template_ehrbase(
    request: Request, auth: str, url_base: str, template: str
):
    logger = get_logger(request)
    logger.debug("inside post_template_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        headers = {
            "Authorization": auth,
            "Content-Type": "application/XML",
        }
        params = {"format": "xml"}
        myurl = url_normalize(url_base + "definition/template/adl1.4/")
        response = await fetch_post_data(
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
