from fastapi import APIRouter, HTTPException, Request, Depends, Query
from app.security import verify_jwt_token, get_token_from_header
from uuid import UUID
from app.utils import get_logger
from app.utils import insertlogline
from fastapi.responses import JSONResponse
from app.backend_ehrbase.ehr.ehr import (
    get_ehr_by_ehrid_ehrbase,
    get_ehr_by_sid_sns_ehrbase,
    post_ehr_by_ehrid_ehrbase,
    post_ehr_by_sid_sns_ehrbase,
    post_ehr_by_ehrstatus_ehrbase,
    put_ehrstatus_ehrbase,
    get_ehrstatus_ehrbase,
)
import redis
from app.dependencies.redis_dependency import get_redis_client
from typing import Optional
import json
from app.models.ehr.ehr import EhrStatusPost, EhrStatusGetPut
from datetime import datetime
from app.models.ehr.ehr import VersionedObjectId

router = APIRouter()


@router.get("/{ehrid}")
async def get_ehr_by_ehrid(
    request: Request,
    ehrid: UUID,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside get_ehr_by_ehrid")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        ehrid = str(ehrid)
        url_base = request.app.state.url_base
        response = await get_ehr_by_ehrid_ehrbase(request, auth, url_base, ehrid)
        insertlogline(
            redis_client, "Get EHR by ehrid: ehr " + ehrid + " retrieved successfully"
        )
        return JSONResponse(content={"ehr": response["ehr"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during get_ehr_by_ehrid: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(redis_client, "Get EHR by ehrid: ehr " + ehrid + " not found")
            return JSONResponse(content={"ehr": e.__dict__}, status_code=e.status_code)
        else:
            print(f"An exception occurred during get_ehr_by_ehrid: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during get_ehr_by_ehrid"
            )


@router.get("/subjectid/{subjectid}/subjectnamespace/{subjectnamespace}")
async def get_ehr_by_sid_sns(
    request: Request,
    subjectid: str,
    subjectnamespace: str,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside get_ehr_by_sid_sns")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        url_base = request.app.state.url_base
        response = await get_ehr_by_sid_sns_ehrbase(
            request, auth, url_base, subjectid, subjectnamespace
        )
        insertlogline(
            redis_client,
            f"Get EHR by subjectid={subjectid} and subjectnamespace={subjectnamespace}: ehr "
            + response["ehrid"]
            + " retrieved successfully",
        )
        return JSONResponse(content={"ehr": response["ehr"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during get_ehr_by_sid_sns: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                f"Get EHR by subjectid={subjectid} and subjectnamespace={subjectnamespace}: ehr not found",
            )
            return JSONResponse(content={"ehr": e.__dict__}, status_code=e.status_code)
        else:
            print(
                f"An exception occurred during get_ehr_by_subjectid_subjectnamespace: {e}"
            )
            raise HTTPException(
                status_code=500,
                detail="Server error during get_ehr_by_subjectid_subjectnamespace",
            )


@router.post("/ehrstatus")
async def post_ehr_by_ehrstatus(
    request: Request,
    data: EhrStatusPost,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside post_ehr_by_ehrstatus")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        ehrstatus = data.ehrstatus
        print(ehrstatus)
        logger.debug(f"ehrstatus={ehrstatus}")
        ehrstatusjson = json.loads(ehrstatus)
        ehrstatus = json.dumps(ehrstatusjson)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    try:
        url_base = request.app.state.url_base
        response = await post_ehr_by_ehrstatus_ehrbase(
            request, auth, url_base, ehrstatus
        )
        ehrid = response["ehrid"]
        insertlogline(
            redis_client,
            "Post EHR by ehrstatus: ehr " + str(ehrid) + " posted successfully",
        )
        responsetext = "Successfully posted ehrstatus. ehrid=" + str(response["ehrid"])
        return JSONResponse(content={"ehr": responsetext}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during post_ehr_by_ehrstatus: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(redis_client, "Post EHR by ehrstatus: not successful")
            return JSONResponse(content={"ehr": e.__dict__}, status_code=e.status_code)
        else:
            print(f"An exception occurred during post_ehr_by_ehrstatus: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during post_ehr_by_ehrstatus"
            )


@router.get("/{ehrid}/ehrstatus")
async def get_ehrstatus(
    request: Request,
    ehrid: UUID,
    data: Optional[str] = Query(None),
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside get_ehrstatus")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    option = 0
    try:
        if data == None or data == "":
            option = 1
        elif "::" in data:  # determine if data is a valid versionedId
            try:
                VersionedObjectId(data)
                option = 3
            except ValueError:
                pass
        else:  # determine if data is a valid date
            try:
                datetime.fromisoformat(data)
                option = 2
            except ValueError:
                pass

        if option == 0:
            raise HTTPException(status_code=400)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid data")
    try:
        logger.debug(f"data={data}")
        logger.debug(f"option={option}")
        logger.debug(f"ehrid={ehrid}")
        ehrid = str(ehrid)
        url_base = request.app.state.url_base
        response = await get_ehrstatus_ehrbase(
            request, auth, url_base, ehrid, data, option
        )
        if option == 1:
            insertlogline(
                redis_client,
                "Get EHR ehrstatus: ehrid=" + ehrid + " retrieved successfully",
            )
        elif option == 2:
            insertlogline(
                redis_client,
                "Get EHR ehrstatus: ehrid="
                + ehrid
                + " and date="
                + data
                + " retrieved successfully",
            )
        else:
            insertlogline(
                redis_client,
                "Get EHR ehrstatus: ehrid="
                + ehrid
                + " and versionedId="
                + data
                + " retrieved successfully",
            )
        return JSONResponse(
            content={"ehrstatus": response["ehrstatus"]}, status_code=200
        )
    except Exception as e:
        logger.error(f"An exception occurred during get_ehrstatus: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(redis_client, "Get EHR ehrstatus: not successful")
            return JSONResponse(content={"ehr": e.__dict__}, status_code=e.status_code)
        else:
            print(f"An exception occurred during get_ehrstatus: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during get_ehrstatus"
            )


@router.put("/ehrstatus")
async def put_ehrstatus(
    request: Request,
    data: EhrStatusGetPut,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside put_ehrstatus")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        ehrstatus = data.ehrstatus
        ehrid = str(data.ehrid)
        ehrstatusVersionedId = str(data.ehrstatusVersionedId)
        logger.debug(f"ehrstatus={ehrstatus}")
        logger.debug(f"ehrid={ehrid}")
        logger.debug(f"ehrstatusVersionedId={ehrstatusVersionedId}")
        ehrstatusjson = json.loads(ehrstatus)
        ehrstatus = json.dumps(ehrstatusjson)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    try:
        url_base = request.app.state.url_base
        response = await put_ehrstatus_ehrbase(
            request, auth, url_base, ehrstatus, ehrid, ehrstatusVersionedId
        )
        insertlogline(
            redis_client,
            "Put EHR ehrstatus: ehrid="
            + ehrid
            + " ehrstatusVersionedId="
            + str(ehrstatusVersionedId)
            + " posted successfully",
        )
        responsetext = (
            "Successfully modified ehrstatus for EHR with ehrid="
            + ehrid
            + " ehrstatusVersionedId="
            + ehrstatusVersionedId
        )
        return JSONResponse(content={"ehr": responsetext}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during put_ehrstatus: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(redis_client, "Put EHR ehrstatus: not successful")
            return JSONResponse(content={"ehr": e.__dict__}, status_code=e.status_code)
        else:
            print(f"An exception occurred during put_ehrstatus: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during put_ehrstatus"
            )


@router.post("/")
async def post_ehr_by_ehrid_without(
    request: Request,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside post_ehr_by_ehrid without")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        ehrid = ""
        url_base = request.app.state.url_base
        response = await post_ehr_by_ehrid_ehrbase(request, auth, url_base, ehrid)
        ehrid = response["ehrid"]
        insertlogline(
            redis_client, "Post EHR by ehrid: ehr " + ehrid + " posted successfully"
        )
        return JSONResponse(content={"ehr": response["ehr"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during post_ehr_by_ehrid_without: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                "Post EHR by ehrid without ehrid: ehr " + ehrid + " not successful",
            )
            return JSONResponse(content={"ehr": e.__dict__}, status_code=e.status_code)
        else:
            print(f"An exception occurred during post_ehr_by_ehrid_without: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during post_ehr_by_ehrid_without"
            )


@router.post("/{ehrid}")
async def post_ehr_by_ehrid_with(
    request: Request,
    ehrid: UUID,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside post_ehr_by_ehrid_with")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        ehrid = str(ehrid)
        url_base = request.app.state.url_base
        response = await post_ehr_by_ehrid_ehrbase(request, auth, url_base, ehrid)
        ehrid = response["ehrid"]
        insertlogline(
            redis_client, "Post EHR by ehrid: ehr " + ehrid + " posted successfully"
        )
        return JSONResponse(content={"ehr": response["ehr"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during post_ehr_by_ehrid_with: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client, "Post EHR by ehrid: ehr " + ehrid + " not successful"
            )
            return JSONResponse(content={"ehr": e.__dict__}, status_code=e.status_code)
        else:
            print(f"An exception occurred during post_ehr_by_ehrid_with: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during post_ehr_by_ehrid_with"
            )


@router.post("/{ehrid}/subjectid/{subjectid}/subjectnamespace/{subjectnamespace}")
async def post_ehr_by_sid_sns_with(
    request: Request,
    subjectid: str,
    subjectnamespace: str,
    ehrid: UUID,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside post_ehr_by_sid_sns_with")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        ehrid = str(ehrid)
        url_base = request.app.state.url_base
        response = await post_ehr_by_sid_sns_ehrbase(
            request, auth, url_base, ehrid, subjectid, subjectnamespace
        )
        ehrid = response["ehrid"]
        insertlogline(
            redis_client,
            "Post EHR by subjectid and subjectnamespace: ehr "
            + ehrid
            + " subjectid="
            + subjectid
            + " and subjectnamespace="
            + subjectnamespace
            + " posted successfully",
        )
        return JSONResponse(content={"ehr": response["ehr"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during post_ehr_by_sid_sns_with: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                f"Post EHR by subjectid and subjectnamespace: subjectid={subjectid} and subjectnamespace={subjectnamespace} not successful",
            )
            return JSONResponse(content={"ehr": e.__dict__}, status_code=e.status_code)
        else:
            print(f"An exception occurred during post_ehr_by_sid_sns_with: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during post_ehr_by_sid_sns_with"
            )


@router.post("/subjectid/{subjectid}/subjectnamespace/{subjectnamespace}")
async def post_ehr_by_sid_sns_without(
    request: Request,
    subjectid: str,
    subjectnamespace: str,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside post_ehr_by_sid_sns_without")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        ehrid = ""
        url_base = request.app.state.url_base
        response = await post_ehr_by_sid_sns_ehrbase(
            request, auth, url_base, ehrid, subjectid, subjectnamespace
        )
        ehrid = response["ehrid"]
        insertlogline(
            redis_client,
            "Post EHR by subjectid and subjectnamespace: ehr "
            + ehrid
            + " subjectid="
            + subjectid
            + " and subjectnamespace="
            + subjectnamespace
            + " posted successfully",
        )
        return JSONResponse(content={"ehr": response["ehr"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during post_ehr_by_sid_sns_without: {e}")
        if e.status_code == 404:
            insertlogline(
                redis_client,
                f"Post EHR by subjectid and subjectnamespace: subjectid={subjectid} and subjectnamespace={subjectnamespace} not successful",
            )
            return JSONResponse(content={"ehr": e.__dict__}, status_code=404)
        else:
            print(f"An exception occurred during post_ehr_by_sid_sns_without: {e}")
            raise HTTPException(
                status_code=500,
                detail="Server error during post_ehr_by_sid_sns_without",
            )
