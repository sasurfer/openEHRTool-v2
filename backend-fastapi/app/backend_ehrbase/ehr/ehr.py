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


async def get_ehr_by_ehrid_ehrbase(
    request: Request, auth: str, url_base: str, ehrid: str
):
    logger = get_logger(request)
    logger.debug("inside get_ehr_by_ehrid_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        myurl = url_normalize(url_base + "ehr/" + ehrid)
        headers = {
            "Authorization": auth,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Prefer": "return={representation|minimal}",
        }
        response = await fetch_get_data(
            client=client, url=myurl, headers=headers, timeout=20000
        )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            myresp["ehr"] = json.loads(response.text)
        return myresp


async def get_ehr_by_sid_sns_ehrbase(
    request: Request, auth: str, url_base: str, subjectid: str, subjectnamespace: str
):
    logger = get_logger(request)
    logger.debug("inside get_ehr_by_sid_sns_ehrbase")
    async with httpx.AsyncClient() as client:
        myurl = url_normalize(url_base + "ehr")
        myresp = {}
        headers = {
            "Authorization": auth,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Prefer": "return={representation|minimal}",
        }
        params = {"subject_id": subjectid, "subject_namespace": subjectnamespace}
        response = await fetch_get_data(
            client=client, url=myurl, headers=headers, params=params, timeout=20000
        )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            myresp["ehr"] = json.loads(response.text)
            myresp["ehrid"] = myresp["ehr"]["ehr_id"]["value"]
        return myresp


async def post_ehr_by_ehrid_ehrbase(
    request: Request, auth: str, url_base: str, ehrid: str
):
    logger = get_logger(request)
    logger.debug("inside post_ehr_by_ehrid_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        headers = {
            "Authorization": auth,
            "Content-Type": "application/JSON",
            "Accept": "application/json",
            "Prefer": "return={representation|minimal}",
        }
        if ehrid:
            myurl = url_normalize(url_base + "ehr/" + ehrid)
            response = await fetch_put_data(
                client=client, url=myurl, headers=headers, timeout=20000
            )
        else:
            myurl = url_normalize(url_base + "ehr")
            response = await fetch_post_data(
                client=client, url=myurl, headers=headers, timeout=20000
            )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            myresp["ehrid"] = response.headers["ETag"].replace('"', "")
            myresp["ehr"] = {"status": myresp["status"], "ehrid": myresp["ehrid"]}
        return myresp


async def post_ehr_by_sid_sns_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    ehrid: str,
    subjectid: str,
    subjectnamespace: str,
):
    logger = get_logger(request)
    logger.debug("inside post_ehr_by_sid_sns_ehrbase")
    body1 = """
    {
    "_type" : "EHR_STATUS",
    "name" : {
        "_type" : "DV_TEXT",
        "value" : "EHR Status"
    },
    "subject" : {
        "_type" : "PARTY_SELF",
        "external_ref" : {
            "_type" : "PARTY_REF",
    """
    body2 = f'   "namespace" : "{subjectnamespace}",'
    body3 = """
            "type" : "PERSON",
            "id" : {
            "_type" : "GENERIC_ID",
    """
    body4 = f'	"value" : "{subjectid}",\n'
    body5 = """
          "scheme" : "id_scheme"
            }
        }
    },
    "archetype_node_id" : "openEHR-EHR-EHR_STATUS.generic.v1",
    "is_modifiable" : true,
    "is_queryable" : true
    }
    """
    async with httpx.AsyncClient() as client:
        myresp = {}
        headers = {
            "Authorization": auth,
            "Content-Type": "application/JSON",
            "Accept": "application/json",
            "Prefer": "return={representation|minimal}",
        }
        body = body1 + body2 + body3 + body4 + body5
        if ehrid:
            myurl = url_normalize(url_base + "ehr/" + ehrid)
            response = await fetch_put_data(
                client=client, url=myurl, headers=headers, timeout=20000, data=body
            )
        else:
            myurl = url_normalize(url_base + "ehr")
            response = await fetch_post_data(
                client=client, url=myurl, headers=headers, timeout=20000, data=body
            )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            myresp["ehrid"] = response.headers["ETag"].replace('"', "")
            myresp["ehr"] = {"status": myresp["status"], "ehrid": myresp["ehrid"]}
        return myresp


async def post_ehr_by_ehrstatus_ehrbase(
    request: Request, auth: str, url_base: str, ehrstatus: str
):
    logger = get_logger(request)
    logger.debug("inside post_ehr_by_ehrstatus_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        headers = {
            "Authorization": auth,
            "Content-Type": "application/JSON",
            "Accept": "application/json",
            "Prefer": "return={representation|minimal}",
        }
        myurl = url_normalize(url_base + "ehr")
        response = await fetch_post_data(
            client=client, url=myurl, headers=headers, data=ehrstatus, timeout=20000
        )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            myresp["ehrid"] = response.headers["ETag"].replace('"', "")
            myresp["ehr"] = {"status": myresp["status"], "ehrid": myresp["ehrid"]}
        return myresp


async def put_ehrstatus_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    ehrstatus: str,
    ehrid: str,
    ehrstatusversion: str,
):
    logger = get_logger(request)
    logger.debug("inside put_ehrstatus_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        params = {"format": "RAW"}
        headers = {
            "Authorization": auth,
            "Content-Type": "application/JSON",
            "Accept": "application/json",
            "Prefer": "return={representation|minimal}",
            "If-Match": ehrstatusversion,
        }
        myurl = url_normalize(url_base + "ehr/" + ehrid + "/ehr_status")
        response = await fetch_put_data(
            client=client, url=myurl, headers=headers, data=ehrstatus, timeout=20000
        )
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            myresp["ehr"] = {
                "status": myresp["status"],
                "ehrid": ehrid,
                "ehrstatusVersionedId": ehrstatusversion,
            }
        return myresp


async def get_ehrstatus_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    ehrid: str,
    data: str,
    option: int,
):
    logger = get_logger(request)
    logger.debug("inside get_ehrstatus_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        myurl = url_normalize(url_base + "ehr/" + ehrid + "/ehr_status")
        params = {}
        headers = {"Authorization": auth, "Content-Type": "application/json"}
        if option == 3:  # data=versionedid
            myurl = url_normalize(url_base + "ehr/" + ehrid + "/ehr_status/" + data)
        elif option == 2:  # data=version_at_time
            params = {"version_at_time": data}
        logger.debug("myurl: %s", myurl)
        logger.debug("params: %s", params)
        logger.debug("headers: %s", headers)
        logger.debug("option: %s", option)
        logger.debug("data: %s", data)
        response = await fetch_get_data(
            client=client, url=myurl, headers=headers, params=params, timeout=20000
        )
        # logger.debug(f"response.text={response.text}")
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            myresp["ehrstatus"] = json.loads(response.text)
        return myresp


async def get_ehrstatus_versioned_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    ehrid: str,
    data: str,
    option: int,
):
    logger = get_logger(request)
    logger.debug("inside get_ehrstatus_versioned_ehrbase")
    async with httpx.AsyncClient() as client:
        myresp = {}
        myurl = url_normalize(url_base + "ehr/" + ehrid + "/versioned_ehr_status")
        params = {}
        headers = {"Authorization": auth, "Content-Type": "application/json"}
        if option == 2:
            myurl = url_normalize(
                url_base + "ehr/" + ehrid + "/versioned_ehr_status/revision_history"
            )
        if option == 4:  # data=versionedid
            myurl = url_normalize(
                url_base + "ehr/" + ehrid + "/versioned_ehr_status/version/" + data
            )
        elif option == 3:  # data=version_at_time
            myurl = url_normalize(
                url_base + "ehr/" + ehrid + "/versioned_ehr_status/version"
            )
            params = {"version_at_time": data}
        elif option == 5:
            myurl = url_normalize(
                url_base + "ehr/" + ehrid + "/versioned_ehr_status/version"
            )
        logger.debug("myurl: %s", myurl)
        logger.debug("params: %s", params)
        logger.debug("headers: %s", headers)
        logger.debug("option: %s", option)
        logger.debug("data: %s", data)
        response = await fetch_get_data(
            client=client, url=myurl, headers=headers, params=params, timeout=20000
        )
        # logger.debug(f"response.text={response.text}")
        response.raise_for_status()
        myresp["status_code"] = response.status_code
        if 200 <= response.status_code < 210:
            myresp["status"] = "success"
            myresp["ehrstatus"] = json.loads(response.text)
        return myresp
