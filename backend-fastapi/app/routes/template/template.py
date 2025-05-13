from fastapi import APIRouter, HTTPException, Request, Depends, Query
from app.security import verify_jwt_token, get_token_from_header
from uuid import UUID
from app.utils import get_logger
from app.utils import insertlogline
from fastapi.responses import JSONResponse
from app.backend_ehrbase.template.template import (
    get_templates_ehrbase,
    get_template_ehrbase,
    post_template_ehrbase,
)
import redis
from app.dependencies.redis_dependency import get_redis_client
from typing import Optional
import json
from app.models.template.template import (
    get_template_enum_value,
    TemplatePost,
)
from datetime import datetime
from lxml import etree

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
            insertlogline(
                redis_client, "Get templates: templates could not be retrieved"
            )
            return JSONResponse(
                content={"template": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during get_templates: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during get_templates"
            )


@router.get("/")
async def get_template(
    request: Request,
    templateid: str = Query(...),
    format: str = Query(...),
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
                redis_client,
                "Get template: template {template_id} could not be retrieved",
            )
            return JSONResponse(
                content={"template": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during get_template: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during get_template"
            )


@router.post("/")
async def post_template(
    request: Request,
    data: TemplatePost,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside post_template")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    template = data.template
    logger.debug(f"template: {template}")
    try:
        xml_bytes = template.encode("utf-8")
        root = etree.fromstring(xml_bytes)
        namespaces = {"ns": "http://schemas.openehr.org/v1"}
        templateid = root.xpath(
            "//ns:template_id/ns:value/text()", namespaces=namespaces
        )[0]
        template = etree.tostring(root)
    except Exception as e:
        logger.error(f"unable to read templateid: {e}")
        raise HTTPException(
            status_code=400, detail="Unable to read template id from template"
        )

    try:
        url_base = request.app.state.url_base
        response = await post_template_ehrbase(request, auth, url_base, template)
        insertlogline(
            redis_client,
            f"Post template: template {templateid} posted successfully",
        )
        templatetext = {"template_id": templateid, "status": response["status"]}
        return JSONResponse(content={"template": templatetext}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during post_template: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                "Post template: template could not be inserted successfully",
            )
            return JSONResponse(
                content={"template": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during post_template: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during post_template"
            )
