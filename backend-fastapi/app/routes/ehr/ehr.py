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
    get_ehrstatus_versioned_ehrbase,
    post_directory_ehrbase,
    put_directory_ehrbase,
    get_directory_ehrbase,
)
import redis
from app.dependencies.redis_dependency import get_redis_client
from typing import Optional
import json
from app.models.ehr.ehr import (
    VersionedObjectId,
    EhrStatusPost,
    EhrStatusGetPut,
    DirectoryPost,
    DirectoryPut,
)
from datetime import datetime

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

        # Insert ehrid into redis list for fast retrieval
        redis_client.rpush("key_ehrs", ehrid)
        logger.debug("Data inserted into Redis")

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
        if data == "" or data == None:
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
                "Get EHR ehrstatus: ehrstatus for ehrid="
                + ehrid
                + " retrieved successfully",
            )
        elif option == 2:
            insertlogline(
                redis_client,
                "Get EHR ehrstatus: ehrstatus for ehrid="
                + ehrid
                + " and date="
                + data
                + " retrieved successfully",
            )
        else:
            insertlogline(
                redis_client,
                "Get EHR ehrstatus: ehrstatus for ehrid="
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
            if option == 1:
                insertlogline(
                    redis_client,
                    "Get EHR ehrstatus: ehrstatus for ehrid="
                    + ehrid
                    + " not successful",
                )
            elif option == 2:
                insertlogline(
                    redis_client,
                    "Get EHR ehrstatus: ehrstatus for ehrid="
                    + ehrid
                    + " and date="
                    + data
                    + " not successful",
                )
            elif option == 3:
                insertlogline(
                    redis_client,
                    "Get EHR ehrstatus: ehrstatus for ehrid="
                    + ehrid
                    + " and versionedId="
                    + data
                    + " not successful",
                )
            else:
                insertlogline(
                    redis_client,
                    "Get EHR ehrstatus: not successful",
                )

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

        # Insert ehrid into redis list for fast retrieval
        redis_client.rpush("key_ehrs", ehrid)
        logger.debug("Data inserted into Redis")

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
        # Insert ehrid into redis list for fast retrieval
        redis_client.rpush("key_ehrs", ehrid)
        logger.debug("Data inserted into Redis")

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

        # Insert ehrid into redis list for fast retrieval
        redis_client.rpush("key_ehrs", ehrid)
        logger.debug("Data inserted into Redis")

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

        # Insert ehrid into redis list for fast retrieval
        redis_client.rpush("key_ehrs", ehrid)
        logger.debug("Data inserted into Redis")

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


@router.get("/{ehrid}/vehrstatus")
async def get_ehrstatus_versioned(
    request: Request,
    ehrid: UUID,
    data: Optional[str] = Query(None),
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside get_ehrstatus_versioned")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    option = 0
    try:
        if data == "":
            option = 5
        elif data == "versionedinfo":
            option = 1
        elif data == "versionedhistory":
            option = 2
        elif "::" in data:  # determine if data is a valid versionedId
            try:
                VersionedObjectId(data)
                option = 4
            except ValueError:
                pass
        else:  # determine if data is a valid date
            try:
                datetime.fromisoformat(data)
                option = 3
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
        response = await get_ehrstatus_versioned_ehrbase(
            request, auth, url_base, ehrid, data, option
        )
        if option == 1:
            insertlogline(
                redis_client,
                "Get EHR ehrstatus versioned: info for ehrid="
                + ehrid
                + " retrieved successfully",
            )
        elif option == 2:
            insertlogline(
                redis_client,
                "Get EHR ehrstatus versioned: history for ehrid="
                + ehrid
                + " retrieved successfully",
            )
        elif option == 3:
            insertlogline(
                redis_client,
                "Get EHR ehrstatus versioned: ehrstatus forehrid="
                + ehrid
                + " and date="
                + data
                + " retrieved successfully",
            )
        else:
            insertlogline(
                redis_client,
                "Get EHR ehrstatus versioned: ehrstatus for ehrid="
                + ehrid
                + " and versionedId="
                + data
                + " retrieved successfully",
            )
        return JSONResponse(
            content={"ehrstatus": response["ehrstatus"]}, status_code=200
        )
    except Exception as e:
        logger.error(f"An exception occurred during get_ehrstatus_versioned: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(redis_client, "Get EHR ehrstatus versioned: not successful")
            return JSONResponse(content={"ehr": e.__dict__}, status_code=e.status_code)
        else:
            print(f"An exception occurred during get_ehrstatus_versioned: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during get_ehrstatus_versioned"
            )


@router.post("/{ehrid}/directory")
async def post_directory(
    request: Request,
    folder: DirectoryPost,
    ehrid: UUID,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside post_directory")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        ehrid = str(ehrid)
        logger.debug(f"ehrid={ehrid}")
        folder = folder.directory
        logger.debug(f"folder={folder}")
        folderjson = json.loads(folder)
        folder = json.dumps(folderjson)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    try:
        url_base = request.app.state.url_base
        response = await post_directory_ehrbase(request, auth, url_base, ehrid, folder)
        insertlogline(
            redis_client,
            "Post EHR directory folder: Directory folder for ehr "
            + ehrid
            + " posted successfully",
        )

        return JSONResponse(content={"folder": response["json"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during post_directory: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(redis_client, "Post EHR directory folder: not successful")
            return JSONResponse(
                content={"folder": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during post_directory: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during post_directory"
            )


@router.put("/{ehrid}/directory")
async def put_directory(
    request: Request,
    data: DirectoryPut,
    ehrid: UUID,
    redis_client: redis.StrictRedis = Depends(get_redis_client),
    token: str = Depends(get_token_from_header),
):
    logger = get_logger(request)
    logger.debug("inside put_directory")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        ehrid = str(ehrid)
        logger.debug(f"ehrid={ehrid}")
        folder = data.directory
        logger.debug(f"folder={folder}")
        versionedid = str(data.directoryVersionedId)
        logger.debug(f"versionedid={versionedid}")
        folderjson = json.loads(folder)
        folder = json.dumps(folderjson)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    try:
        url_base = request.app.state.url_base
        response = await put_directory_ehrbase(
            request, auth, url_base, ehrid, folder, versionedid
        )
        insertlogline(
            redis_client,
            "Put EHR directory folder: Directory folder for ehr "
            + ehrid
            + " updated successfully",
        )

        return JSONResponse(content={"folder": response["json"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during put_directory: {e}")
        if 400 <= e.status_code < 500:
            insertlogline(
                redis_client,
                "Put EHR directory folder: Directory folder update for ehr"
                + ehrid
                + " not successful",
            )
            return JSONResponse(
                content={"folder": e.__dict__}, status_code=e.status_code
            )
        else:
            print(f"An exception occurred during put_directory: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during put_directory"
            )


@router.get("/{ehrid}/directory")
async def get_directory(
    request: Request,
    ehrid: UUID,
    data: Optional[str] = Query(None),
    path: Optional[str] = Query(None),
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
    logger.debug(f"dddddddata={data}")
    try:
        if data == "" or data == None:
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
        response = await get_directory_ehrbase(
            request, auth, url_base, ehrid, data, path, option
        )
        if option == 1:
            insertlogline(
                redis_client,
                "Get EHR directory: directory for ehrid="
                + ehrid
                + " retrieved successfully",
            )
        elif option == 2:
            insertlogline(
                redis_client,
                "Get EHR directory: directory for ehrid="
                + ehrid
                + " and date="
                + data
                + " retrieved successfully",
            )
        else:
            insertlogline(
                redis_client,
                "Get EHR directory: directory for ehrid="
                + ehrid
                + " and versionedId="
                + data
                + " retrieved successfully",
            )
        return JSONResponse(content={"folder": response["json"]}, status_code=200)
    except Exception as e:
        logger.error(f"An exception occurred during get_directory: {e}")
        if 400 <= e.status_code < 500:
            if option == 1:
                insertlogline(
                    redis_client, f"Get EHR directory: not successful for ehr {ehrid}"
                )
            elif option == 2:
                insertlogline(
                    redis_client,
                    f"Get EHR directory: not successful for ehr {ehrid} and date {data}",
                )
            elif option == 3:
                insertlogline(
                    redis_client,
                    f"Get EHR directory: not successful for ehr {ehrid} and versionedId {data}",
                )
            else:
                insertlogline(redis_client, "Get EHR directory: not successful")
            return JSONResponse(content={"ehr": e.__dict__}, status_code=e.status_code)
        else:
            print(f"An exception occurred during get_directory: {e}")
            raise HTTPException(
                status_code=500, detail="Server error during get_directory"
            )
