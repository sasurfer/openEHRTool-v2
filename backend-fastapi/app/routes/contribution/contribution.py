from fastapi import APIRouter, HTTPException, Request, Depends, Query
from app.security import verify_jwt_token, get_token_from_header
from uuid import UUID
from app.utils import get_logger
from app.utils import insertlogline
from fastapi.responses import JSONResponse

from app.backend_ehrbase.contribution.contribution import (
    get_contribution_ehrbase,
    post_contribution_ehrbase,
)
import redis
from app.dependencies.redis_dependency import get_redis_client
from typing import Optional
import json
from app.models.contribution.contribution import (
    get_contribution_enum_value,
    ContributionPost,
)

from app.models import VersionedObjectId
from datetime import datetime
from lxml import etree

router = APIRouter()


@router.post("/")
async def post_contribution(
    request: Request,
    data: ContributionPost,
    ehrid: UUID = Query(None),
    format: str = Query(None),
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside post_contribution")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    contribution = data.contribution
    logger.debug(f"contribution: {contribution}")
    format = get_contribution_enum_value(format)
    if format == "xml":
        try:
            xml_bytes = contribution.encode("utf-8")
            root = etree.fromstring(xml_bytes)
            composition = etree.tostring(root)
        except Exception as e:
            logger.error(f"unable to read contribution: {e}")
            raise HTTPException(status_code=400, detail="Unable to read contribution")
    else:
        try:
            contributionjson = json.loads(contribution)
            contribution = json.dumps(contributionjson)
        except Exception as e:
            logger.error(f"unable to read contribution: {e}")
            raise HTTPException(status_code=400, detail="Unable to read contribution")
    try:
        url_base = request.app.state.url_base
        ehrid = str(ehrid)
        response = await post_contribution_ehrbase(
            request,
            auth,
            url_base,
            ehrid,
            contribution,
            format,
        )
        contributionid = response["contributionid"]
        insertlogline(
            redis_client,
            f"Post contribution: contribution= {contributionid},for ehrid={ehrid}, posted successfully",
        )

        return JSONResponse(
            content={"contribution": response["contribution"]}, status_code=200
        )
    except Exception as e:
        logger.error(f"An exception occurred during post_contribution: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                f"Post contribution: contribution, for ehrid={ehrid}, could not be inserted successfully",
            )
            return JSONResponse(
                content={"contribution": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during post_contribution: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during post_contribution"
            )


@router.get("/{contributionid}")
async def get_contribution(
    request: Request,
    contributionid: str,
    ehrid: UUID = Query(None),
    format: str = Query(None),
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside get_contribution")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        contributionid = contributionid.replace("%3A", ":")
        if ":" in contributionid:
            VersionedObjectId(contributionid)
        else:
            UUID(contributionid)
    except Exception as e:
        logger.error(f"Invalid contributionid: {contributionid}")
        raise HTTPException(status_code=400, detail="Invalid contributionid")

    try:
        ehrid = str(ehrid)
        url_base = request.app.state.url_base
        url_base_ecis = request.app.state.url_base_ecis
        ehrbase_version = request.app.state.ehrbase_version
        format = get_contribution_enum_value(format)
        response = await get_contribution_ehrbase(
            request,
            auth,
            url_base,
            contributionid,
            ehrid,
            format,
        )
        insertlogline(
            redis_client,
            f"Get contribution: contributionid={contributionid} ehrid={ehrid} and format={format} retrieved successfully",
        )
        return JSONResponse(
            content={"contribution": response["contribution"]}, status_code=200
        )
    except Exception as e:
        logger.error(f"An exception occurred during get_contribution: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                f"Get contribution: contributionid={contributionid} ehrid={ehrid} and format={format} could not be retrieved",
            )
            return JSONResponse(
                content={"contribution": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during get_contribution: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during get_contribution"
            )
