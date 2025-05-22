from fastapi import FastAPI, HTTPException, Depends, Request
from url_normalize import url_normalize
import json
import httpx
import asyncio
from app.dependencies.redis_dependency import get_redis_client
from app.backend_redis.myredis import get_redis_status
import redis
from app.utils import get_logger
from app.backend_ehrbase import fetch_get_data, fetch_post_data


async def get_sidebar_ehrs_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
):
    logger = get_logger(request)
    logger.debug("Inside get_sidebar_ehrs_ehrbase")
    async with httpx.AsyncClient() as client:
        if redis_client:
            redistatus = get_redis_status(redis_client)
            if (
                redistatus == "ok"
                and redis_client.exists("key_ehrs")
                and redis_client.llen("key_ehrs") > 0
            ):
                # Retrieve data from Redis
                logger.debug("Retrieving data from Redis")
                ehrs = redis_client.lrange("key_ehrs", 0, -1)
                return ehrs
        logger.debug("Retrieving data from EHRBase server")

        # Retrieve data from EHRBase server
        ehrs = []
        # Get ehrs
        myurl = url_normalize(url_base + "query/aql")
        data = {}
        aqltext = "select e/ehr_id/value FROM EHR e"
        data["q"] = aqltext
        headers = {"Authorization": auth, "Content-Type": "application/json"}
        response = await fetch_post_data(
            client=client, url=myurl, headers=headers, data=json.dumps(data)
        )

        if 199 < response.status_code < 210:
            ehrs_rows = json.loads(response.text)["rows"]
            ehrs = [t[0] for t in ehrs_rows]

            if redis_client and get_redis_status(redis_client) == "ok":
                redis_client.delete("key_ehrs")
                redis_client.lpush("key_ehrs", *ehrs)
        else:
            ehrs = ["Unavailable"]
        return ehrs


async def get_sidebar_templates_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
):
    logger = get_logger(request)
    logger.debug("inside get_sidebar_templates")
    async with httpx.AsyncClient() as client:
        # if redis_client:
        #     redistatus = get_redis_status(redis_client)
        #     if (
        #         redistatus == "ok"
        #         and redis_client.exists("key_templates")
        #         and redis_client.llen("key_templates") > 0
        #     ):
        #         # Retrieve data from Redis
        #         logger.debug("Retrieving data from Redis")
        #         templates = redis_client.lrange("key_templates", 0, -1)
        #         templates = [json.loads(t) for t in templates]
        #         print(f"templates: {templates}")
        #         return templates
        logger.debug("Retrieving data from EHRBase server")
        # retrieve data from EHRBase server
        templates = []
        # get templates
        myurl = url_normalize(url_base + "definition/template/adl1.4")
        headers = {"Authorization": auth, "Content-Type": "application/json"}
        params = {"format": "JSON"}
        response = await fetch_get_data(
            client=client, url=myurl, headers=headers, params=params
        )
        if 199 < response.status_code < 210:
            templates = json.loads(response.text)
            if redis_client and get_redis_status(redis_client) == "ok":
                redis_client.delete("key_templates")
                for t in templates:
                    print(t)
                    redis_client.lpush("key_templates", json.dumps(t))
        else:
            return ["Unavailable"]
        return templates


async def get_sidebar_compositions_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
):
    logger = get_logger(request)
    logger.debug("Inside get_sidebar_compositions_ehrbase")
    async with httpx.AsyncClient() as client:
        if redis_client:
            redistatus = get_redis_status(redis_client)
            if (
                redistatus == "ok"
                and redis_client.exists("key_compositions")
                and redis_client.llen("key_compositions") > 0
            ):
                # retrieve data from redis
                print("GGGGGGGGGGGGG")
                logger.debug("GGGGGGGGGG")
                compositions = redis_client.lrange("key_compositions", 0, -1)
                return compositions
        print("HHHHHHHHHHHHHH")
        logger.debug("HHHHHHHHHHHH")
        # retrieve data from EHRBase server
        compositions = []
        # get compositions
        myurl = url_normalize(url_base + "/query/aql")
        data = {}
        aqltext = "SELECT c/uid/value,e/ehr_id/value FROM EHR e CONTAINS COMPOSITION c"
        data["q"] = aqltext
        headers = {"Authorization": auth, "Content-Type": "application/json"}
        response = await fetch_post_data(
            client=client, url=myurl, headers=headers, data=json.dumps(data)
        )
        compositions = {}
        if 199 < response.status_code < 210:
            comp_rows = json.loads(response.text)["rows"]
            compositions = [str(c[0]) + " # " + str(c[1]) for c in comp_rows]
            if redis_client and get_redis_status(redis_client) == "ok":
                redis_client.delete("key_compositions")
                redis_client.lpush("key_compositions", *compositions)
        else:
            compositions = ["Unavailable"]
        return compositions


async def get_sidebar_queries_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
):
    logger = get_logger(request)
    logger.debug("inside get_sidebar_queries")
    async with httpx.AsyncClient() as client:
        if redis_client:
            redistatus = get_redis_status(redis_client)
            if (
                redistatus == "ok"
                and redis_client.exists("key_queries")
                and redis_client.llen("key_queries") > 0
            ):
                # retrieve data from redis
                print("GGGGGGGGGGGGG")
                logger.debug("GGGGGGGGGG")
                queries = redis_client.lrange("key_queries", 0, -1)
                queries = [json.loads(q) for q in queries]
                print(f"queries: {queries}")
                return queries
        print("HHHHHHHHHHHHHH")
        logger.debug("HHHHHHHHHHHH")
        # retrieve data from EHRBase server
        queries = []
        # get queries
        myurl = url_normalize(url_base + "/definition/query/")
        headers = {"Authorization": auth, "Content-Type": "application/json"}
        response = await fetch_get_data(client=client, url=myurl, headers=headers)
        print(response.status_code)
        if 199 < response.status_code < 210:
            queries = json.loads(response.text)["versions"]
            if redis_client and get_redis_status(redis_client) == "ok":
                redis_client.delete("key_queries")
                for q in queries:
                    redis_client.lpush("key_queries", json.dumps(q))
        else:
            return ["Unavailable"]
        return queries
