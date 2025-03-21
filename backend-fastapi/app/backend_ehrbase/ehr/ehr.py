from fastapi import FastAPI, HTTPException, Depends, Request
from url_normalize import url_normalize
import json
import httpx
from app.dependencies.redis_dependency import get_redis_client
from app.backend_redis.myredis import get_redis_status
import redis
from app.utils import get_logger
from app.backend_ehrbase import fetch_get_data, fetch_post_data

async def get_ehr_by_ehrid_ehrbase(request: Request,auth : str,url_base: str,ehrid: str):
    logger=get_logger(request)
    logger.debug('inside get_ehr_by_ehrid_ehrbase')
    async with httpx.AsyncClient() as client:
        myresp={}
        myurl=url_normalize(url_base  + 'ehr/'+ehrid)
        headers={'Authorization':auth, 
            'Content-Type':'application/json','Accept': 'application/json','Prefer': 'return={representation|minimal}'}
        response = await fetch_get_data(client=client,url=myurl,headers=headers,timeout=20000 )
        response.raise_for_status()  
        myresp['status_code']=response.status_code
        if 200 <= response.status_code < 210:
            myresp['status']="success"
            myresp["ehr"]=json.loads(response.text)
        return myresp

async def get_ehr_by_sid_sns_ehrbase(request: Request,auth : str,url_base: str,subjectid: str,subjectnamespace: str):
    logger=get_logger(request)
    logger.debug('inside get_ehr_by_sid_sns_ehrbase')
    async with httpx.AsyncClient() as client:
        myurl=url_normalize(url_base  + 'ehr')
        myresp={}
        headers={'Authorization':auth, 
            'Content-Type':'application/json','Accept': 'application/json','Prefer': 'return={representation|minimal}'}
        params={'subject_id':subjectid,'subject_namespace':subjectnamespace}
        response = await fetch_get_data(client=client,url=myurl,headers=headers,params=params,timeout=20000 )
        response.raise_for_status()  
        myresp['status_code']=response.status_code
        if 200 <= response.status_code < 210:
            myresp['status']="success"
            myresp["ehr"]=json.loads(response.text)
            myresp['ehrid']=myresp['ehr']['ehr_id']['value']
        return myresp
