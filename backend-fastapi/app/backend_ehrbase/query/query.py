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
from urllib.parse import quote_plus


async def get_queries_ehrbase(request: Request, auth: str, url_base: str):
    logger = get_logger(request)
    logger.debug("inside get_queries_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        myurl = url_normalize(url_base + "definition/query")
        params = {}
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
            queriesinfo = json.loads(response.text)
            ntv = {}
            queries = set()
            for q in queriesinfo["versions"]:
                logger.debug(f"q={q}")
                queries.add(q["name"])
                if q["name"] in ntv:
                    ntv[q["name"]].append(q["version"])
                else:
                    ntv[q["name"]] = [q["version"]]

            queries = list(queries)
            myresp["query"] = {
                "queriesinfo": queriesinfo,
                "queries": queries,
                "nametoversions": ntv,
            }
            logger.debug(f"myresp={myresp}")
        return myresp


async def get_query_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    queryname: str,
    version: str,
):
    logger = get_logger(request)
    logger.debug("inside get_query_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        params = {}
        if version:
            myurl = url_normalize(
                url_base + "definition/query/" + queryname + "/" + version
            )
        else:
            myurl = url_normalize(url_base + "definition/query/" + queryname)

        headers = {
            "Authorization": auth,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        response = await fetch_get_data(
            client=client, url=myurl, headers=headers, timeout=20000, params=params
        )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            myresp["query"] = json.loads(response.text)
        return myresp


async def put_query_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    q: str,
    queryname: str,
    version: str,
    qtype: str,
):
    logger = get_logger(request)
    logger.debug("inside put_query_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        params = {"type": qtype, "format": "RAW"}
        if version:
            myurl = url_normalize(
                url_base + "definition/query/" + queryname + "/" + version
            )
        else:
            myurl = url_normalize(url_base + "definition/query/" + queryname)

        headers = {
            "Authorization": auth,
            "Content-Type": "text/plain",
        }
        logger.debug(f"myurl={myurl}")
        logger.debug(f"q={q}")
        logger.debug(f"headers={headers}")
        logger.debug(f"params={params}")
        logger.debug(f"queryname={queryname}")
        logger.debug(f"version={version}")
        logger.debug(f"qtype={qtype}")
        response = await fetch_put_data(
            client=client,
            url=myurl,
            headers=headers,
            timeout=20000,
            params=params,
            data=q,
        )
        logger.debug(f"response={response}")
        logger.debug(f"response.text={response.text}")
        logger.debug(f"response.status_code={response.status_code}")
        logger.debug(f"response.headers={response.headers}")
        logger.debug(f"response.content={response.content}")
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            logger.debug(f"response.headers={response.headers}")
            if not version:
                version = response.headers["Location"].split("::")[1].split("/")[1]
            saved = response.headers["date"]
            myresp["query"] = {
                "name": queryname,
                "version": version,
                "saved": saved,
                "qtype": qtype,
                "status": "success",
            }
        return myresp


async def runstored_query_get_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    queryname: str,
    version: str,
    fetch: int,
    offset: int,
    queryparams: str,
):
    logger = get_logger(request)
    logger.debug("inside runstored_query_get_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        params = {}
        myurl = url_normalize(url_base + "query/" + queryname + "/" + version)
        headers = {
            "Authorization": auth,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if fetch:
            params["fetch"] = fetch
        if offset:
            params["offset"] = offset
        if queryparams:
            params["query_parameters"] = queryparams.replace(",", "&")
        response = await fetch_get_data(
            client=client, url=myurl, headers=headers, timeout=20000, params=params
        )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            myresp["query"] = json.loads(response.text)
        return myresp


async def runstored_query_post_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    queryname: str,
    version: str,
    fetch: int,
    offset: int,
    queryparams: str,
):
    logger = get_logger(request)
    logger.debug("inside runstored_query_post_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        data = {}
        params = {}
        myurl = url_normalize(url_base + "query/" + queryname + "/" + version)
        headers = {
            "Authorization": auth,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if fetch:
            data["fetch"] = fetch
        if offset:
            data["offset"] = offset
        if queryparams:
            qplist = queryparams.split(",")
            myqp = {}
            for qp in qplist:
                key = qp.split("=")[0]
                value = qp.split("=")[1]
                try:
                    val = int(value)
                except ValueError:
                    val = value
                myqp[key] = val
                data["query_parameters"] = myqp
        response = await fetch_post_data(
            client=client,
            url=myurl,
            headers=headers,
            timeout=20000,
            params=params,
            data=json.dumps(data),
        )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            myresp["query"] = json.loads(response.text)
        return myresp


async def run_query_get_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    q: str,
    fetch: int,
    offset: int,
    queryparams: str,
):
    logger = get_logger(request)
    logger.debug("inside run_query_get_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        params = {}
        myurl = url_normalize(url_base + "query/aql")
        headers = {
            "Authorization": auth,
            "Content-Type": "application/json",
        }
        if "$" in q:
            q.replace("$", quote_plus("$"))
        params["q"] = q
        if fetch:
            params["fetch"] = fetch
        if offset:
            params["offset"] = offset
        if queryparams:
            params["query_parameters"] = queryparams.replace(",", "&")
        response = await fetch_get_data(
            client=client, url=myurl, headers=headers, timeout=20000, params=params
        )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            myresp["query"] = json.loads(response.text)
        return myresp


async def run_query_post_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    q: str,
    fetch: int,
    offset: int,
    queryparams: str,
):
    logger = get_logger(request)
    logger.debug("inside run_query_post_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        data = {}
        params = {}
        myurl = url_normalize(url_base + "query/aql")
        headers = {
            "Authorization": auth,
            "Content-Type": "application/json",
        }
        data["q"] = q
        if fetch:
            data["fetch"] = fetch
        if offset:
            data["offset"] = offset
        if queryparams:
            qplist = queryparams.split(",")
            myqp = {}
            for qp in qplist:
                key = qp.split("=")[0]
                value = qp.split("=")[1]
                try:
                    val = int(value)
                except ValueError:
                    val = value
                myqp[key] = val
                data["query_parameters"] = myqp
        response = await fetch_post_data(
            client=client,
            url=myurl,
            headers=headers,
            timeout=20000,
            params=params,
            data=json.dumps(data),
        )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            myresp["query"] = json.loads(response.text)
        return myresp
