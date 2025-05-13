import json
import httpx
from fastapi import FastAPI, HTTPException, Depends, Request
from url_normalize import url_normalize
import redis
from app.backend_ehrbase import fetch_get_data, fetch_post_data
from app.utils import get_logger


async def get_dashboard_data_ehrbase(
    request: Request,
    auth: str,
    url_base: str,
    url_base_status: str,
    url_base_management: str,
    app: FastAPI = Depends(),
):
    logger = get_logger(request)
    logger.debug("inside get_dashboard data ehrbase")
    async with httpx.AsyncClient() as client:
        print("dashboard data")
        metrics = {}
        barData = {}
        pieData = {}
        # get metrics: ehrsInUse, ehrsCount, compositionsCount, templatesInUse,templatesCount, aqlsCount
        myurl = url_normalize(url_base + "/definition/query/")
        print(myurl)
        # aqlsCount
        headers = {"Authorization": auth, "Content-Type": "application/json"}
        response = await fetch_get_data(client=client, url=myurl, headers=headers)
        print(response.status_code)
        if 199 < response.status_code < 210:
            aqls = json.loads(response.text)["versions"]
            metrics["aqlsCount"] = len(aqls)
        else:
            metrics["aqlsCount"] = "Unavailable"
        # ehrsCount
        myurl = url_normalize(url_base + "/query/aql")
        data = {}
        aqltext = "SELECT e/ehr_id/value FROM EHR e"
        data["q"] = aqltext
        headers = {"Authorization": auth, "Content-Type": "application/json"}
        response = await fetch_post_data(
            client=client, url=myurl, headers=headers, data=json.dumps(data)
        )
        if 199 < response.status_code < 210:
            ehrs = json.loads(response.text)["rows"]
            metrics["ehrsCount"] = len(ehrs)
        else:
            metrics["ehrsCount"] = "Unavailable"
        # templatesInUse
        # ehrsInUse,compositionsCount,templatesInUse
        myurl = url_normalize(url_base + "/query/aql")
        data = {}
        aqltext = "SELECT e/ehr_id/value,c/uid/value,c/archetype_details/template_id/value FROM EHR e CONTAINS COMPOSITION c"
        data["q"] = aqltext
        headers = {"Authorization": auth, "Content-Type": "application/json"}
        response = await fetch_post_data(
            client=client, url=myurl, headers=headers, data=json.dumps(data)
        )
        ehrs_in_use = set()
        templates_in_use = set()
        compositions = {}
        if 199 < response.status_code < 210:
            compositions = json.loads(response.text)["rows"]
            metrics["compositionsCount"] = len(compositions)
            # compute ehrsInUse,templatesInUse
            ehrs_in_use = set(r[0] for r in compositions)
            metrics["ehrsInUse"] = len(ehrs_in_use)
            templates_in_use = set(r[2] for r in compositions)
            metrics["templatesInUse"] = len(templates_in_use)
        else:
            metrics["compositionsCount"] = "Unavailable"
            metrics["ehrsInUse"] = "Unavailable"
            metrics["templatesInUse"] = "Unavailable"
        # get metrics: templatesCount
        # templatesCount
        myurl = url_normalize(url_base + "/definition/template/adl1.4")
        params = {"format": "JSON"}
        headers = {"Authorization": auth, "Content-Type": "application/XML"}
        response = await fetch_get_data(
            client=client, url=myurl, headers=headers, params=params
        )
        if 199 < response.status_code < 210:
            templates = json.loads(response.text)
            metrics["templatesCount"] = len(templates)
        else:
            metrics["templatesCount"] = "Unavailable"
        # get barData==#ehrs (Y) for a given #compositions (X)
        barData = {}
        if ehrs_in_use and compositions:
            c = [0] * len(ehrs_in_use)
            for i, e in enumerate(ehrs_in_use):
                c[i] = 0
                for r in compositions:
                    if r[0] == e:
                        c[i] += 1
            cpe = {i: c.count(i) for i in c}

            barData = cpe
        # get pieData==compositions per template
        pieData = {}
        if templates_in_use and compositions:
            d = {}
            for i, t in enumerate(templates_in_use):
                for r in compositions:
                    if r[2] == t:
                        if t in d:
                            d[t] += 1
                        else:
                            d[t] = 1
            pieData = d
            # percentage in new pieData
            total_compositions = len(compositions)
            for k, v in pieData.items():
                pieData[k] = round((v / total_compositions) * 100, 2)
        # get info
        # info from status
        myurl = url_normalize(url_base_status)
        headers = {
            "Authorization": auth,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        response = await fetch_get_data(
            client=client, url=url_base_status, headers=headers
        )
        info = {"status": "Unavailable"}
        if 199 < response.status_code < 210:
            info = response.json()
        return metrics, barData, pieData, info
