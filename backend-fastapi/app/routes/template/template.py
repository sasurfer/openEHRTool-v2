from fastapi import APIRouter, HTTPException, Request, Depends, Query
from app.security import verify_jwt_token, get_token_from_header
from uuid import UUID
from app.utils import get_logger
from app.utils import insertlogline
from fastapi.responses import JSONResponse
from app.backend_ehrbase.template.template import (
    get_templates_ehrbase,
    get_template_ehrbase,
)
import redis
from app.dependencies.redis_dependency import get_redis_client
from typing import Optional
import json
from app.models.ehr.ehr import (
    get_template_enum_value,
)
from datetime import datetime

router = APIRouter()


@router.get("/templates")
async def get_templates(
    request: Request,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside get_templates")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        url_base = request.app.state.url_base
        response = await get_templates_ehrbase(request, auth, url_base)
        insertlogline(redis_client, "Get templates: templates retrieved successfully")
        return JSONResponse(content={"template": response["template"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during get_templates: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(redis_client, "Get templates: templates not retrieved")
            return JSONResponse(content={"ehr": e.__dict__}, status_code=e.status_code)
        else:
            print(f"An exception occurred during get_templates: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during get_templates"
            )


@router.get("/")
async def get_template(
    request: Request,
    templateid: str = Query(None),
    format: str = Query(None),
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside get_template")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        format = get_template_enum_value(format)
        logger.debug(f"format: {format}")
        url_base = request.app.state.url_base
        url_base_ecis = request.app.state.url_base_ecis
        ehrbase_version = request.app.state.ehrbase_version
        response = await get_template_ehrbase(
            request, auth, url_base, url_base_ecis, templateid, format, ehrbase_version
        )
        insertlogline(
            redis_client, f"Get template: template {templateid} retrieved successfully"
        )
        return JSONResponse(content={"template": response["template"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during get_template: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client, "Get template: template {template_id} not retrieved"
            )
            return JSONResponse(content={"ehr": e.__dict__}, status_code=e.status_code)
        else:
            print(f"An exception occurred during get_template: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during get_template"
            )
