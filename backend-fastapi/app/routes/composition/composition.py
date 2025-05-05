from fastapi import APIRouter, HTTPException, Request, Depends, Query
from app.security import verify_jwt_token, get_token_from_header
from uuid import UUID
from app.utils import get_logger
from app.utils import insertlogline
from fastapi.responses import JSONResponse

from app.backend_ehrbase.composition.composition import (
    get_composition_ehrbase,
    post_composition_ehrbase,
    put_composition_ehrbase,
)
import redis
from app.dependencies.redis_dependency import get_redis_client
from typing import Optional
import json
from app.models.composition.composition import (
    get_composition_enum_value,
    CompositionPost,
)
from app.models import VersionedObjectId
from datetime import datetime
from lxml import etree

router = APIRouter()


@router.post("/")
async def post_composition(
    request: Request,
    data: CompositionPost,
    ehrid: UUID = Query(None),
    templateid: str = Query(None),
    format: str = Query(None),
    check: Optional[bool] = Query(None),
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside post_composition")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    composition = data.composition
    logger.debug(f"composition: {composition}")
    format = get_composition_enum_value(format)
    if format == "xml":
        try:
            xml_bytes = composition.encode("utf-8")
            root = etree.fromstring(xml_bytes)
            composition = etree.tostring(root)
        except Exception as e:
            logger.error(f"unable to read composition: {e}")
            raise HTTPException(status_code=400, detail="Unable to read composition")
    else:
        try:
            compositionjson = json.loads(composition)
            composition = json.dumps(compositionjson)
        except Exception as e:
            logger.error(f"unable to read composition: {e}")
            raise HTTPException(status_code=400, detail="Unable to read composition")
    try:
        url_base = request.app.state.url_base
        url_base_ecis = request.app.state.url_base_ecis
        ehrbase_version = request.app.state.ehrbase_version
        ehrid = str(ehrid)
        response = await post_composition_ehrbase(
            request,
            auth,
            url_base,
            url_base_ecis,
            ehrid,
            templateid,
            composition,
            format,
            ehrbase_version,
            check,
        )
        compositionid = response["compositionid"]
        insertlogline(
            redis_client,
            f"Post composition: composition= {compositionid},for templateid={templateid} and ehrid={ehrid}, posted successfully",
        )
        # update redis composition list
        new_element = compositionid + " # " + ehrid
        redis_client.rpush("key_compositions", new_element)

        return JSONResponse(
            content={"composition": response["composition"]}, status_code=200
        )
    except Exception as e:
        logger.error(f"An exception occurred during post_composition: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                f"Post composition: composition, for templateid={templateid} and ehrid={ehrid}, not inserted successfully",
            )
            return JSONResponse(
                content={"composition": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during post_composition: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during post_composition"
            )


@router.put("/{compositionvid}")
async def put_composition(
    request: Request,
    compositionvid: str,
    data: CompositionPost,
    ehrid: UUID = Query(None),
    templateid: str = Query(None),
    format: str = Query(None),
    check: Optional[bool] = Query(None),
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside put_composition")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    composition = data.composition
    logger.debug(f"composition: {composition}")
    format = get_composition_enum_value(format)
    compositionvid = compositionvid.replace("%3A", ":")
    try:
        VersionedObjectId(compositionvid)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Invalid composition versioned id format"
        )

    if format == "xml":
        try:
            xml_bytes = composition.encode("utf-8")
            root = etree.fromstring(xml_bytes)
            composition = etree.tostring(root)
        except Exception as e:
            logger.error(f"unable to read composition: {e}")
            raise HTTPException(status_code=400, detail="Unable to read composition")
    else:
        try:
            compositionjson = json.loads(composition)
            composition = json.dumps(compositionjson)
        except Exception as e:
            logger.error(f"unable to read composition: {e}")
            raise HTTPException(status_code=400, detail="Unable to read composition")
    try:
        url_base = request.app.state.url_base
        url_base_ecis = request.app.state.url_base_ecis
        ehrbase_version = request.app.state.ehrbase_version
        ehrid = str(ehrid)
        response = await put_composition_ehrbase(
            request,
            auth,
            url_base,
            url_base_ecis,
            ehrid,
            templateid,
            composition,
            format,
            ehrbase_version,
            check,
            compositionvid,
        )
        insertlogline(
            redis_client,
            f"Post composition: composition= {compositionvid},for templateid={templateid} and ehrid={ehrid}, updated successfully",
        )
        # update redis composition list
        new_element = response["compositionvid"] + " # " + ehrid
        redis_client.rpush("key_compositions", new_element)

        return JSONResponse(
            content={"composition": response["composition"]}, status_code=200
        )
    except Exception as e:
        logger.error(f"An exception occurred during put_composition: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                f"Put composition: composition, for templateid={templateid} and ehrid={ehrid}, not updated successfully",
            )
            return JSONResponse(
                content={"composition": e.__dict__}, status_code=e.status_code
            )
        else:
            raise HTTPException(
                status_code=500, detail="Server error during put_composition"
            )


@router.get("/{compositionid}")
async def get_composition(
    request: Request,
    compositionid: str,
    ehrid: UUID = Query(None),
    format: str = Query(None),
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside get_composition")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        compositionid = compositionid.replace("%3A", ":")
        if ":" in compositionid:
            VersionedObjectId(compositionid)
        else:
            UUID(compositionid)
    except Exception as e:
        logger.error(f"Invalid compositionid: {compositionid}")
        raise HTTPException(status_code=400, detail="Invalid compositionid")

    try:
        ehrid = str(ehrid)
        url_base = request.app.state.url_base
        url_base_ecis = request.app.state.url_base_ecis
        ehrbase_version = request.app.state.ehrbase_version
        format = get_composition_enum_value(format)
        response = await get_composition_ehrbase(
            request,
            auth,
            url_base,
            url_base_ecis,
            compositionid,
            ehrid,
            format,
            ehrbase_version,
        )
        insertlogline(
            redis_client,
            f"Get composition: composition compid={compositionid} ehrid={ehrid} and format={format} retrieved successfully",
        )
        return JSONResponse(
            content={"composition": response["composition"]}, status_code=200
        )
    except Exception as e:
        logger.error(f"An exception occurred during get_composition: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                f"Get composition: composition compid={compositionid} ehrid={ehrid} and format={format} not retrieved",
            )
            return JSONResponse(
                content={"template": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during get_composition: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during get_composition"
            )
