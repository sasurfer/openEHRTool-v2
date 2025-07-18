from fastapi import APIRouter, HTTPException, Request, Depends, Query
from app.security import verify_jwt_token, get_token_from_header
from uuid import UUID
from app.utils import get_logger
from app.utils import insertlogline
from fastapi.responses import JSONResponse

from app.backend_ehrbase.query.query import (
    get_queries_ehrbase,
    get_query_ehrbase,
    put_query_ehrbase,
    runstored_query_get_ehrbase,
    runstored_query_post_ehrbase,
    run_query_get_ehrbase,
    run_query_post_ehrbase,
)
import redis
from app.dependencies.redis_dependency import get_redis_client
from typing import Optional
import json
from app.models.query.query import AQLVersion, AQLName

from datetime import datetime
from lxml import etree

router = APIRouter()


@router.get("/query")
async def get_queries(
    request: Request,
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside get_queries")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        url_base = request.app.state.url_base
        response = await get_queries_ehrbase(request, auth, url_base)
        return JSONResponse(content={"query": response["query"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during get_queries: {e}")
        if 400 <= e.status_code < 500:
            return JSONResponse(
                content={"query": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during get_queries: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during get_queries"
            )


@router.get("/")
async def get_query(
    request: Request,
    queryname: str = Query(...),
    version: Optional[str] = Query(None),
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside get_query")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        if version != None:
            AQLVersion(root=version)
    except Exception as e:
        logger.error(f"An exception occurred during checkversion: {e}")
        raise HTTPException(
            status_code=400, detail="Invalid version format. Must be like 1.0.0 "
        )
    try:
        AQLName(name=queryname)
    except Exception as e:
        logger.error(f"An exception occurred during checkqueryname: {e}")
        raise HTTPException(
            status_code=400,
            detail="Invalid query name format. Must be like org.ehrbase.local::myquery",
        )

    try:
        url_base = request.app.state.url_base
        response = await get_query_ehrbase(request, auth, url_base, queryname, version)
        if version:
            insertlogline(
                redis_client,
                f"Get query: query {queryname} version {version} retrieved successfully",
            )
        else:
            insertlogline(
                redis_client,
                f"Get query: query versions for {queryname}  retrieved successfully",
            )
        return JSONResponse(content={"query": response["query"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during get_query: {e}")
        if 400 <= e.status_code < 500:
            if version:
                insertlogline(
                    redis_client,
                    f"Get query: query {queryname} version {version} could not be retrieved",
                )
            else:
                insertlogline(
                    redis_client,
                    f"Get query: query versions for {queryname} could not be retrieved",
                )
            return JSONResponse(
                content={"query": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during get_query: {e}")
            raise HTTPException(status_code=500, detail="Server error during get_query")


@router.put("/")
async def put_query(
    request: Request,
    q: str = Query(...),
    queryname: str = Query(...),
    version: str = Query(...),
    qtype: str = Query(...),
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside put_query")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        if version != None and version != "":
            AQLVersion(root=version)
    except Exception as e:
        logger.error(f"An exception occurred during checkversion: {e}")
        raise HTTPException(
            status_code=400, detail="Invalid version format. Must be like 1.0.0 "
        )
    try:
        AQLName(name=queryname)
    except Exception as e:
        logger.error(f"An exception occurred during checkqueryname: {e}")
        raise HTTPException(
            status_code=400,
            detail="Invalid query name format. Must be like org.ehrbase.local::myquery",
        )

    try:
        url_base = request.app.state.url_base
        q = q.translate({ord(c): " " for c in "\n\r"})
        response = await put_query_ehrbase(
            request, auth, url_base, q, queryname, version, qtype
        )
        if not version:
            version = response["query"]["version"]
        insertlogline(
            redis_client,
            f"Put query: query {queryname} version {version} inserted successfully",
        )
        # update redis query list
        # new_element = (
        #     response["query"]["name"]
        #     + " "
        #     + response["query"]["version"]
        #     + " "
        #     + response["query"]["saved"]
        # )
        new_element = {
            "name": response["query"]["name"],
            "version": response["query"]["version"],
            "saved": response["query"]["saved"],
        }
        # redis_client.rpush("key_queries", new_element)
        redis_client.rpush("key_queries", json.dumps(new_element))
        return JSONResponse(content={"query": response["query"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during put_query: {e}")
        if 400 <= e.status_code < 500:
            if version:
                insertlogline(
                    redis_client,
                    f"Put query: query {queryname} version {version} could not be inserted",
                )
            else:
                insertlogline(
                    redis_client,
                    f"Get query: query{queryname} could not be inserted",
                )
            return JSONResponse(
                content={"query": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during put_query: {e}")
            raise HTTPException(status_code=500, detail="Server error during put_query")


@router.get("/runstored")
async def runstored_query_get(
    request: Request,
    queryname: str = Query(...),
    version: AQLVersion = Query(...),
    fetch: Optional[int] = Query(None),
    offset: Optional[int] = Query(None),
    queryparams: Optional[str] = Query(None),
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside runstored_query_get")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        version = version.root
        if queryparams:
            queryparams = queryparams.replace("%3D", "=").replace("%2C", ",")
        url_base = request.app.state.url_base
        response = await runstored_query_get_ehrbase(
            request, auth, url_base, queryname, version, fetch, offset, queryparams
        )
        insertlogline(
            redis_client,
            f"Run (Get) query stored: ran query {queryname} version {version}  successfully",
        )
        return JSONResponse(content={"query": response["query"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during runstored_query_get: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                f"Run (Get) query stored: query {queryname} version {version} ran unsuccessfully",
            )
            return JSONResponse(
                content={"query": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during runstored_query_get: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during runstored_query_get"
            )


@router.post("/runstored")
async def runstored_query_post(
    request: Request,
    queryname: str = Query(...),
    version: AQLVersion = Query(...),
    fetch: Optional[int] = Query(None),
    offset: Optional[int] = Query(None),
    queryparams: Optional[str] = Query(None),
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside runstored_query_post")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        version = version.root
        if queryparams:
            queryparams = queryparams.replace("%3D", "=").replace("%2C", ",")
        url_base = request.app.state.url_base
        response = await runstored_query_post_ehrbase(
            request, auth, url_base, queryname, version, fetch, offset, queryparams
        )
        insertlogline(
            redis_client,
            f"Run (Post) query stored: ran query {queryname} version {version}  successfully",
        )
        return JSONResponse(content={"query": response["query"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during runstored_query_post: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                f"Run (Post) query stored: query {queryname} version {version} ran unsuccessfully",
            )
            return JSONResponse(
                content={"query": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during runstored_query_post: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during runstored_query_post"
            )


@router.get("/run")
async def run_query_get(
    request: Request,
    q: str = Query(...),
    fetch: Optional[int] = Query(None),
    offset: Optional[int] = Query(None),
    queryparams: Optional[str] = Query(None),
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside run_query_get")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        if queryparams:
            queryparams = queryparams.replace("%3D", "=").replace("%2C", ",")
        url_base = request.app.state.url_base
        response = await run_query_get_ehrbase(
            request, auth, url_base, q, fetch, offset, queryparams
        )
        insertlogline(
            redis_client,
            f"Run (Get) query: ran query={q} successfully",
        )
        return JSONResponse(content={"query": response["query"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during run_query_get: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                f"Run (Get) query: query {q} ran unsuccessfully",
            )
            return JSONResponse(
                content={"query": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during run_query_get: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during run_query_get"
            )


@router.post("/run")
async def run_query_post(
    request: Request,
    q: str = Query(...),
    fetch: Optional[int] = Query(None),
    offset: Optional[int] = Query(None),
    queryparams: Optional[str] = Query(None),
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside run_query_post")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        url_base = request.app.state.url_base
        response = await run_query_post_ehrbase(
            request, auth, url_base, q, fetch, offset, queryparams
        )
        insertlogline(
            redis_client,
            f"Run (Post) query: ran query={q} successfully",
        )
        return JSONResponse(content={"query": response["query"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during run_query_post: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                f"Run (Post) query: query {q} ran unsuccessfully",
            )
            return JSONResponse(
                content={"query": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during run_query_post: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during run_query_post"
            )
