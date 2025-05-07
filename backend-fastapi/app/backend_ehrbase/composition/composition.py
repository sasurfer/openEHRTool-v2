from fastapi import FastAPI, HTTPException, Depends, Request
from url_normalize import url_normalize
import json
import httpx
from app.dependencies.redis_dependency import get_redis_client
from app.backend_redis.myredis import get_redis_status
import redis
from app.utils import get_logger
from app.backend_ehrbase import (
    fetch_get_data,
    fetch_post_data,
    fetch_put_data,
    fetch_delete_data,
)
from lxml import etree
from app.utils import get_logger, compareEhrbaseVersions, composition_check
from fastapi import HTTPException, Request


async def post_composition_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    url_base_ecis: str,
    ehrid: str,
    templateid: str,
    composition: str,
    format: str,
    ehrbase_version: str,
    check: bool,
):
    logger = get_logger(request)
    logger.debug("inside post_composition_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        headers = {
            "Authorization": auth,
            "Prefer": "return=representation",
        }
        myurl = url_normalize(url_base + "ehr/" + ehrid + "/composition")
        if format == "xml":
            headers["Content-Type"] = "application/xml"
            headers["Accept"] = "application/xml"

            params = {"format": "XML"}
        elif format == "json":
            headers["Content-Type"] = "application/json"
            headers["Accept"] = "application/json"
            if compareEhrbaseVersions(ehrbase_version, "2.5.0") > 0:
                params = {"format": "JSON"}
            else:
                params = {"format": "RAW"}
        elif format == "structured":
            headers["Content-Type"] = "application/json"
            headers["Accept"] = "application/json"
            params = {"format": "STRUCTURED", "templateId": templateid, "ehrId": ehrid}
            if compareEhrbaseVersions(ehrbase_version, "2.5.0") <= 0:
                myurl = url_normalize(url_base_ecis + "composition")
        elif format == "flat":
            headers["Content-Type"] = "application/json"
            headers["Accept"] = "application/json"
            headers["Prefer"] = "return=representation"
            params = {"format": "FLAT", "templateId": templateid, "ehrId": ehrid}
            if compareEhrbaseVersions(ehrbase_version, "2.5.0") <= 0:
                myurl = url_normalize(url_base_ecis + "composition")
        else:
            logger.error(f"Invalid enum value: {format}")
            raise HTTPException(status_code=400, detail=f"Invalid enum value: {format}")
        response = await fetch_post_data(
            client=client,
            url=myurl,
            headers=headers,
            data=composition,
            params=params,
            timeout=20000,
        )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            myresp["compositionid"] = response.headers["Location"].split(
                "composition/"
            )[1]
            myresp["composition"] = {
                "status": myresp["status"],
                "compositionid": myresp["compositionid"],
            }
            if check:
                respget = await get_composition_ehrbase(
                    request,
                    auth,
                    url_base,
                    url_base_ecis,
                    myresp["compositionid"],
                    ehrid,
                    format,
                    ehrbase_version,
                )
                if format != "xml":
                    composition_get = json.dumps(respget["composition"])
                else:
                    composition_get = respget["composition"]
                check_outcome = composition_check(composition, composition_get, format)
                if check_outcome == None:
                    myresp["composition"][
                        "check"
                    ] = "Successful. Retrieved and posted composition are the same"
                else:
                    myresp["composition"][
                        "check"
                    ] = "WARNING: Retrieved composition different from posted one"
                    myresp["composition"]["checkinfo"] = check_outcome
                pass
        return myresp


async def put_composition_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    url_base_ecis: str,
    ehrid: str,
    templateid: str,
    composition: str,
    format: str,
    ehrbase_version: str,
    check: bool,
    compositionvid: str,
):
    logger = get_logger(request)
    logger.debug("inside put_composition_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        headers = {
            "Authorization": auth,
            "Prefer": "return=representation",
            "If-Match": compositionvid,
        }
        compositionid = compositionvid.split("::")[0]
        myurl = url_normalize(
            url_base + "ehr/" + ehrid + "/composition/" + compositionid
        )
        if format == "xml":
            headers["Content-Type"] = "application/xml"
            headers["Accept"] = "application/xml"
            params = {"format": "XML"}
        elif format == "json":
            headers["Content-Type"] = "application/json"
            headers["Accept"] = "application/json"
            if compareEhrbaseVersions(ehrbase_version, "2.5.0") > 0:
                params = {"format": "JSON"}
            else:
                params = {"format": "RAW"}
        elif format == "structured":
            headers["Content-Type"] = "application/json"
            headers["Accept"] = "application/json"
            params = {"format": "STRUCTURED", "templateId": templateid, "ehrId": ehrid}
            if compareEhrbaseVersions(ehrbase_version, "2.5.0") <= 0:
                myurl = url_normalize(url_base_ecis + "composition/" + compositionid)
        elif format == "flat":
            headers["Content-Type"] = "application/json"
            headers["Accept"] = "application/json"
            headers["Prefer"] = "return=representation"
            params = {"format": "FLAT", "templateId": templateid, "ehrId": ehrid}
            if compareEhrbaseVersions(ehrbase_version, "2.5.0") <= 0:
                myurl = url_normalize(url_base_ecis + "composition/" + compositionid)
        else:
            logger.error(f"Invalid enum value: {format}")
            raise HTTPException(status_code=400, detail=f"Invalid enum value: {format}")
        response = await fetch_put_data(
            client=client,
            url=myurl,
            headers=headers,
            data=composition,
            params=params,
            timeout=20000,
        )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            compositionvnum = int(compositionvid.split("::")[2]) + 1
            compositionvidnew = (
                compositionvid.split("::")[0]
                + "::"
                + compositionvid.split("::")[1]
                + "::"
                + str(compositionvnum)
            )
            myresp["compositionvid"] = compositionvidnew
            myresp["composition"] = {
                "status": myresp["status"],
                "compositionvid": myresp["compositionvid"],
            }
            if check:
                respget = await get_composition_ehrbase(
                    request,
                    auth,
                    url_base,
                    url_base_ecis,
                    compositionvidnew,
                    ehrid,
                    format,
                    ehrbase_version,
                )
                if format != "xml":
                    composition_get = json.dumps(respget["composition"])
                else:
                    composition_get = respget["composition"]
                check_outcome = composition_check(composition, composition_get, format)
                if check_outcome == None:
                    myresp["composition"][
                        "check"
                    ] = "Successful. Retrieved and posted composition are the same"
                else:
                    myresp["composition"][
                        "check"
                    ] = "WARNING: Retrieved composition different from posted one"
                    myresp["composition"]["checkinfo"] = check_outcome
                pass
        return myresp


async def get_composition_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    url_base_ecis: str,
    compositionid: str,
    ehrid: str,
    format: str,
    ehrbase_version: str,
):
    logger = get_logger(request)
    logger.debug("inside get_composition_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        headers = {
            "Authorization": auth,
            "Prefer": "return=representation",
        }
        myurl = url_normalize(
            url_base + "ehr/" + ehrid + "/composition/" + compositionid
        )
        if format == "xml":
            headers["Accept"] = "application/xml"
            headers["Content-Type"] = "application/xml"
            params = {"format": "XML"}
        elif format == "json":
            headers["Accept"] = "application/json"
            headers["Content-Type"] = "application/json"
            params = {"format": "JSON"}
        elif format == "structured":
            headers["Accept"] = "application/json"
            headers["Content-Type"] = "application/json"
            params = {"format": "STRUCTURED", "ehrId": ehrid}
            if compareEhrbaseVersions(ehrbase_version, "2.5.0") <= 0:
                myurl = url_normalize(url_base_ecis + "composition/" + compositionid)
        elif format == "flat":
            headers["Accept"] = "application/json"
            headers["Content-Type"] = "application/json"
            params = {"format": "FLAT", "ehrId": ehrid}
            if compareEhrbaseVersions(ehrbase_version, "2.5.0") <= 0:
                myurl = url_normalize(url_base_ecis + "composition/" + compositionid)
        else:
            logger.error(f"Invalid enum value: {format}")
            raise HTTPException(status_code=400, detail=f"Invalid enum value: {format}")
        response = await fetch_get_data(
            client=client,
            url=myurl,
            headers=headers,
            params=params,
            timeout=20000,
        )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            composition = ""
            if format == "xml":
                root = etree.fromstring(response.text)
                composition = etree.tostring(
                    root, encoding="unicode", method="xml", pretty_print=True
                )
            elif format == "json":
                composition = json.loads(response.text)
            elif format == "structured":
                if compareEhrbaseVersions(ehrbase_version, "2.5.0") > 0:
                    composition = json.loads(response.text)
                else:
                    composition = json.loads(response.text)["composition"]
            elif format == "flat":
                if compareEhrbaseVersions(ehrbase_version, "2.5.0") > 0:
                    composition = json.loads(response.text)
                else:
                    composition = json.loads(response.text)["composition"]
            else:
                logger.error(f"Invalid enum value: {format}")
                raise HTTPException(
                    status_code=400, detail=f"Invalid enum value: {format}"
                )

            myresp["composition"] = composition
        return myresp


async def get_compositionv_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    compositionid: str,
    ehrid: str,
    option: int,
    data: str,
):
    logger = get_logger(request)
    logger.debug("inside get_compositionv_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        headers = {
            "Authorization": auth,
            "Content-Type": "application/json",
        }
        params = {}
        myurl = url_normalize(
            url_base + "ehr/" + ehrid + "/versioned_composition/" + compositionid
        )
        if option == 1:  # info
            pass
        elif option == 2:  # revision history
            myurl = url_normalize(
                url_base
                + "ehr/"
                + ehrid
                + "/versioned_composition/"
                + compositionid
                + "/revision_history"
            )
        elif option == 3:  # version at time
            params["version_at_time"] = data
            myurl = url_normalize(
                url_base
                + "ehr/"
                + ehrid
                + "/versioned_composition/"
                + compositionid
                + "/version"
            )
        elif option == 4:  # version by version
            myurl = url_normalize(
                url_base
                + "ehr/"
                + ehrid
                + "/versioned_composition/"
                + compositionid
                + "/version/"
                + data
            )
        elif option == 5:  # empty
            myurl = url_normalize(
                url_base
                + "ehr/"
                + ehrid
                + "/versioned_composition/"
                + compositionid
                + "/version"
            )
        else:
            logger.error(f"Invalid option value: {option}")
            raise HTTPException(
                status_code=400, detail=f"Invalid option value: {option}"
            )
        response = await fetch_get_data(
            client=client,
            url=myurl,
            headers=headers,
            params=params,
            timeout=20000,
        )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            myresp["composition"] = json.loads(response.text)
        return myresp


async def delete_composition_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    compositionvid: str,
    ehrid: str,
):
    logger = get_logger(request)
    logger.debug("inside delete_composition_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        headers = {
            "Authorization": auth,
        }
        myurl = url_normalize(
            url_base + "ehr/" + ehrid + "/composition/" + compositionvid
        )
        params = {}
        response = await fetch_delete_data(
            client=client,
            url=myurl,
            headers=headers,
            params=params,
            timeout=20000,
        )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            myresp["composition"] = {
                "status": myresp["status"],
                "action": f"Deleted composition {compositionvid} ehrid {ehrid}",
            }
        return myresp
