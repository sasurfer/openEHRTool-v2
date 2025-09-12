from fastapi import APIRouter, HTTPException, Request, Depends, Query
from app.security import verify_jwt_token, get_token_from_header
from uuid import UUID
from app.utils import get_logger
from app.utils import insertlogline
from fastapi.responses import JSONResponse
from app.backend_ehrbase.admin.template import (
    put_template_admin_ehrbase,
    delete_template_admin_ehrbase,
    delete_templates_admin_ehrbase,
)
from app.backend_ehrbase.admin.ehr import (
    delete_ehr_admin_ehrbase,
    delete_directory_admin_ehrbase,
)
from app.backend_ehrbase.admin.status import (
    get_status_admin_ehrbase,
)
from app.backend_ehrbase.admin.query import (
    delete_query_admin_ehrbase,
)
from app.backend_ehrbase.admin.composition import (
    delete_composition_admin_ehrbase,
)
from app.backend_ehrbase.admin.contribution import (
    put_contribution_admin_ehrbase,
)
import redis
from app.dependencies.redis_dependency import get_redis_client
from typing import Optional
import json
from app.models.template.template import (
    get_template_enum_value,
    TemplatePost,
)
from app.models.contribution.contribution import (
    get_contribution_enum_value,
    ContributionPost,
)
from datetime import datetime
from lxml import etree
from app.models.query.query import AQLVersion, AQLName
from app.backend_redis.myredis import remove_item_from_redis_list
from app.models.ehr.ehr import (
    VersionedObjectId,
)

router = APIRouter()


@router.get("/status")
async def get_admin_status(
    request: Request,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside get_admin_status")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        url_base_admin = request.app.state.url_base_admin
        response = await get_status_admin_ehrbase(request, auth, url_base_admin)
        insertlogline(
            redis_client,
            f"Get admin status: user has admin permissions",
        )
        return JSONResponse(content={"status": response["message"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during get_admin_status: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                f"Get admin status: user does not have admin permissions",
            )
            return JSONResponse(
                content={"status": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during get_admin_status: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during get_admin_status"
            )


@router.put("/template")
async def put_admin_template(
    request: Request,
    data: TemplatePost,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside put_admin_template")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    template = data.template
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
        url_base_admin = request.app.state.url_base_admin
        response = await put_template_admin_ehrbase(
            request, auth, url_base_admin, templateid, template
        )
        insertlogline(
            redis_client,
            f"Put admin template: template {templateid} updated successfully",
        )
        templatetext = {"template_id": templateid, "status": response["status"]}
        return JSONResponse(content={"template": templatetext}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during put_admin_template: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                f"Put admin template: template {templateid} could not be updated successfully",
            )
            return JSONResponse(
                content={"template": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during put_template: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during put_template"
            )


@router.delete("/template")
async def delete_admin_template(
    request: Request,
    template_name: str = Query(...),
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside delete_admin_template")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        url_base_admin = request.app.state.url_base_admin
        response = await delete_template_admin_ehrbase(
            request, auth, url_base_admin, template_name
        )
        insertlogline(
            redis_client,
            f"Delete admin template: template {template_name} deleted successfully",
        )
        return JSONResponse(content={"template": response["template"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during delete_template: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                f"Delete admin template: template {template_name} could not be deleted successfully",
            )
            return JSONResponse(
                content={"template": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during delete_admin_template: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during delete_admin_template"
            )


@router.delete("/templates")
async def delete_admin_templates(
    request: Request,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside delete_admin_templates")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        url_base_admin = request.app.state.url_base_admin
        response = await delete_templates_admin_ehrbase(request, auth, url_base_admin)
        insertlogline(
            redis_client,
            f"Delete admin templates: templates deleted successfully",
        )
        return JSONResponse(
            content={"templates": response["templates"]},
            status_code=200,
        )
    except Exception as e:
        logger.error(f"An exception occurred during delete_admin_templates: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                f"Delete admin templates: templates could not be deleted successfully",
            )
            return JSONResponse(
                content={"template": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during delete_admin_templates: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during delete_admin_templates"
            )


@router.delete("/ehr/{ehrid}")
async def delete_admin_ehr(
    request: Request,
    ehrid: UUID,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside delete_admin_ehr")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        ehrid = str(ehrid)
        url_base_admin = request.app.state.url_base_admin
        response = await delete_ehr_admin_ehrbase(request, auth, url_base_admin, ehrid)
        insertlogline(
            redis_client,
            f"Delete admin ehr: ehr with {ehrid} deleted successfully",
        )
        if redis_client:
            removed = remove_item_from_redis_list(redis_client, "key_ehrs", ehrid)
            if removed:
                logger.debug(f"Removed ehr {ehrid} from Redis")
        return JSONResponse(content={"ehr": response["ehr"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during delete_ehr: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                f"Delete admin ehr: ehr with {ehrid} could not be deleted successfully",
            )
            return JSONResponse(content={"ehr": e.__dict__}, status_code=e.status_code)
        else:
            print(f"An exception occurred during delete_admin_ehr: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during delete_admin_ehr"
            )


@router.delete("/query")
async def delete_admin_query(
    request: Request,
    queryname: str = Query(...),
    version: str = Query(...),
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside delete_admin_query")
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
        url_base_admin = request.app.state.url_base_admin
        response = await delete_query_admin_ehrbase(
            request, auth, url_base_admin, queryname, version
        )
        insertlogline(
            redis_client,
            f"Delete admin query: query={queryname} version={version} deleted successfully",
        )
        if redis_client:
            removed = remove_item_from_redis_list(
                redis_client, "key_queries", queryname, version
            )
            if removed:
                logger.debug(f"Removed query {queryname} version {version} from Redis")
        return JSONResponse(content={"query": response["query"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during delete_query: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                f"Delete admin query: query={queryname} version={version} could not be deleted successfully",
            )
            return JSONResponse(
                content={"query": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during delete_admin_template: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during delete_admin_query"
            )


@router.delete("/ehr/{ehrid}/directory/{directoryid}")
async def delete_directory_admin(
    request: Request,
    ehrid: UUID,
    directoryid: UUID,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside delete_directory admin")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        logger.debug(f"data={directoryid}")
        logger.debug(f"ehrid={ehrid}")
        ehrid = str(ehrid)
        directoryid = str(directoryid)
        url_base_admin = request.app.state.url_base_admin
        response = await delete_directory_admin_ehrbase(
            request, auth, url_base_admin, ehrid, directoryid
        )
        insertlogline(
            redis_client,
            "Delete EHR directory admin: Directory folder for ehrid="
            + ehrid
            + " directoryId="
            + directoryid
            + " deleted successfully",
        )

        return JSONResponse(content={"folder": response["ehr"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during delete_directory_admin: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                f"Delete EHR directory: Directory folder for ehr {ehrid} directoryId {directoryid} could not be deleted",
            )
            return JSONResponse(
                content={"folder": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during delete_directory_admin: {e}")
            raise HTTPException(
                status_code=500,
                detail="Server error during delete_directory_admin",
            )


@router.delete("/ehr/{ehrid}/composition/{compositionid}")
async def delete_admin_composition(
    request: Request,
    ehrid: UUID,
    compositionid: UUID,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside delete_admin_composition")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        ehrid = str(ehrid)
        compositionid = str(compositionid)
        url_base_admin = request.app.state.url_base_admin
        response = await delete_composition_admin_ehrbase(
            request, auth, url_base_admin, ehrid, compositionid
        )
        insertlogline(
            redis_client,
            f"Delete admin composition: composition {compositionid} from ehr {ehrid} deleted successfully",
        )
        if redis_client:
            removed = remove_item_from_redis_list(
                redis_client, "key_compositions", ehrid, compositionid
            )
            if removed:
                logger.debug(
                    f"Removed composition {compositionid} from ehr {ehrid} from Redis"
                )
        return JSONResponse(
            content={"composition": response["composition"]}, status_code=200
        )
    except Exception as e:
        logger.error(f"An exception occurred during delete_composition: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                f"Delete admin composition: composition {compositionid} from ehr {ehrid} could not be deleted successfully",
            )
            return JSONResponse(
                content={"composition": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during delete_admin_composition: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during delete_admin_composition"
            )


@router.put("/contribution/{contributionid}")
async def put_admin_contribution(
    request: Request,
    contributionid: str,
    data: ContributionPost,
    ehrid: UUID = Query(...),
    format: str = Query(...),
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside put_admin_contribution")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    contribution = data.contribution
    format = get_contribution_enum_value(format)
    if format == "xml":
        try:
            xml_bytes = contribution.encode("utf-8")
            root = etree.fromstring(xml_bytes)
            contribution = etree.tostring(root)
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
        contributionid = contributionid.replace("%3A", ":")
        if ":" in contributionid:
            VersionedObjectId(contributionid).replace("%3A", ":")
        else:
            UUID(contributionid)
    except Exception as e:
        logger.error(f"unable to read contributionid: {e}")
        raise HTTPException(
            status_code=400, detail="Unable to read contribution id from contribution"
        )

    try:
        url_base_admin = request.app.state.url_base_admin
        ehrid = str(ehrid)
        response = await put_contribution_admin_ehrbase(
            request, auth, url_base_admin, contributionid, ehrid, contribution, format
        )
        insertlogline(
            redis_client,
            f"Put admin contribution: contribution {contributionid} updated successfully",
        )
        contributiontext = {
            "contribution_id": contributionid,
            "status": response["status"],
        }
        return JSONResponse(content={"contribution": contributiontext}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during put_admin_contribution: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                f"Put admin contribution: contribution {contributionid} could not be updated successfully",
            )
            return JSONResponse(
                content={"contribution": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during put_contribution: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during put_contribution"
            )
