from flask import current_app
from url_normalize import url_normalize
import json
import httpx
import asyncio
from .myredis import get_redis_status
import redis

async def get_dashboard_data_ehrbase(auth,url_base,url_base_status,url_base_management):
    current_app.logger.debug('inside get_dashboard data')  
    async with httpx.AsyncClient() as client:
        print('dashboard data')       
        metrics={}
        barData={}
        pieData={}
        try:
            #get metrics: ehrsInUse, ehrsCount, compositionsCount, templatesInUse,templatesCount, aqlsCount
            myurl=url_normalize(url_base  + '/definition/query/')
            print(myurl)
            #aqlsCount
            response = await client.get(myurl, headers={'Authorization':auth,'Content-Type': 'application/json'}) 
            print(response.status_code)
            if(response.status_code<210 and response.status_code>199):
                aqls=json.loads(response.text)['versions']
                metrics['aqlsCount']=len(aqls)
            else:
                metrics['aqlsCount']='Unavailable'
        except Exception as e:
            print(f"An exception occurred in get_dashboard_data while getting aqlsCount in : {e}")
            current_app.logger.error(f"An error occurred in get_dashboard_data while getting aqlsCount: {e} ")
            raise Exception("An error occurred during dashboard data fetching") from e
        #ehrsCount
        try:
            #ehrsCount
            myurl=url_normalize(url_base  + '/query/aql')
            data={}
            aqltext="SELECT e/ehr_id/value FROM EHR e"
            data['q']=aqltext
            response = await client.post(myurl,headers={'Authorization':auth,'Content-Type': 'application/json'}, data=json.dumps(data))
            if(response.status_code<210 and response.status_code>199):
                ehrs=json.loads(response.text)['rows']
                metrics['ehrsCount']=len(ehrs)
            else:
                metrics['ehrsCount']='Unavailable'
        except Exception as e:
            print(f"An exception occurred in get_dashboard_data while getting ehrsCount in : {e}")
            current_app.logger.error(f"An error occurred in get_dashboard_data while getting ehrsCount: {e} ")
            raise Exception("An error occurred during dashboard data fetching") from e
        try:
            #get metrics: ehrsInUse,compositionsCount,templatesInUse
            #ehrsInUse,compositionsCount,templatesInUse
            myurl=url_normalize(url_base  + '/query/aql')
            data={}
            aqltext="SELECT e/ehr_id/value,c/uid/value,c/archetype_details/template_id/value FROM EHR e CONTAINS COMPOSITION c"
            data['q']=aqltext
            response = await client.post(myurl,headers={'Authorization':auth,'Content-Type': 'application/json'}, data=json.dumps(data))
            ehrs_in_use=set()
            templates_in_use=set()
            compositions={}
            if(response.status_code<210 and response.status_code>199):
                compositions=json.loads(response.text)['rows']
                metrics['compositionsCount']=len(compositions)
                #compute ehrsInUse,templatesInUse
                ehrs_in_use=set(r[0] for r in compositions)
                metrics['ehrsInUse']=len(ehrs)
                templates_in_use=set(r[2] for r in compositions)
                metrics['templatesInUse']=len(templates_in_use)
            else:
                metrics['compositionsCount']='Unavailable'
                metrics['ehrsInUse']='Unavailable'
                metrics['templatesInUse']='Unavailable'
        except Exception as e:
            print(f"An exception occurred in get_dashboard_data while getting ehrsInUse,compositionsCount,templatesInUse in : {e}")
            current_app.logger.error(f"An error occurred in get_dashboard_data while getting ehrsInUse,compositionsCount,templatesInUse: {e}")
            raise Exception("An error occurred during dashboard data fetching") from e
        try:
            #get metrics: templatesCount
            #templatesCount
            myurl=url_normalize(url_base  + '/definition/template/adl1.4')
            response=await client.get(myurl,params={'format': 'JSON'},headers={'Authorization':auth,'Content-Type':'application/XML'})
            if(response.status_code<210 and response.status_code>199):
                templates=json.loads(response.text)
                metrics['templatesCount']=len(templates)
            else:
                metrics['templatesCount']='Unavailable'
            #get barData==#ehrs (Y) for a given #compositions (X)
            barData={}
            if(ehrs_in_use and compositions):
                c=[0]*len(ehrs_in_use)
                for i,e in enumerate(ehrs_in_use):
                    c[i]=0
                    for r in compositions:
                        if(r[0]==e):
                            c[i]+=1
                cpe={i:c.count(i) for i in c}

                barData=cpe 
            #get pieData==compositions per template
            pieData={}
            if(templates_in_use and compositions):
                d={}
                for i,t in enumerate(templates_in_use):
                    for r in compositions:
                        if(r[2]==t):
                            if t in d:
                                d[t]+=1
                            else:
                                d[t]=1 
                pieData=d   
        except Exception as e:
            print(f"An exception occurred in get_dashboard_data while getting templatesCount,barData,pieData in : {e}")
            current_app.logger.error(f"An error occurred in get_dashboard_data while getting templatesCount,barData,pieData: {e}")
            raise Exception("An error occurred during dashboard data fetching") from e
        try:
            #get info
            #info from status
            myurl=url_normalize(url_base_status)
            response = await client.get(url_base_status, headers={'Authorization':auth,'Content-Type':'application/json','Accept': 'application/json'})
            info={'status':'Unavailable'}
            if(response.status_code<210 and response.status_code>199):
                info=response.json()
        except Exception as e:
            print(f"An exception occurred in get_dashboard_data while getting info in : {e}")
            current_app.logger.error(f"An error occurred in get_dashboard_data while getting info: {e} ")
            raise Exception("An error occurred during dashboard data fetching") from e    
        return metrics,barData,pieData,info

async def get_sidebar_ehrs_ehrbase(auth,url_base):
    current_app.logger.debug('inside get_sidebar_ehrs ehrbase')
    async with httpx.AsyncClient() as client:
        r=current_app.config['REDIS_CLIENT']
        if r is not None:
            redistatus=get_redis_status()
            if redistatus=='ok' and r.exists('key_ehrs') and r.llen('key_ehrs')>0:
                #retrieve data from redis
                current_app.logger.debug('GGGGGGGGGG')
                ehrs=r.lrange('key_ehrs',0,-1)
                return ehrs
        current_app.logger.debug('HHHHHHHHHHHH')
        #retrieve data from EHRBase server
        ehrs=[]
        try:
            #get ehrs
            myurl=url_normalize(url_base  + 'query/aql')
            data={}
            aqltext="select e/ehr_id/value FROM EHR e"
            data['q']=aqltext
            response = await client.post(myurl,headers={'Authorization':auth,'Content-Type': 'application/json'}, data=json.dumps(data))
            if(response.status_code<210 and response.status_code>199):
                ehrs_rows=json.loads(response.text)['rows']
                ehrs=[t[0] for t in ehrs_rows]
                if r is not None and get_redis_status()=='ok':
                    r.delete('key_ehrs')
                    r.lpush('key_ehrs',*ehrs)
            else:
                ehrs=['Unavailable']
        except Exception as e:
            print(f"An exception occurred in get_sidebar_ehrs while getting ehrs in : {e}")
            current_app.logger.error(f"An error occurred in get_sidebar_ehrs while getting ehrs: {e} ")
            raise Exception("An error occurred during sidebar ehrs fetching") from e
        return ehrs

async def get_sidebar_templates_ehrbase(auth,url_base):
    current_app.logger.debug('inside get_sidebar_templates')
    async with httpx.AsyncClient() as client:
        r=current_app.config['REDIS_CLIENT']
        if r is not None:
            redistatus=get_redis_status()
            if redistatus=='ok' and r.exists('key_templates') and r.llen('key_templates')>0:
            #retrieve data from redis
                print('GGGGGGGGGGGGG')
                current_app.logger.debug('GGGGGGGGGG')
                templates=r.lrange('key_templates',0,-1)
                templates=[json.loads(t) for t in templates]
                print(f'templates: {templates}')
                return templates
        print('HHHHHHHHHHHHHH')
        current_app.logger.debug('HHHHHHHHHHHH')
        #retrieve data from EHRBase server
        templates=[]
        try:
            #get templates
            myurl=url_normalize(url_base  + 'definition/template/adl1.4')
            response=await client.get(myurl,params={'format': 'JSON'},headers={'Authorization':auth,'Content-Type':'application/json'})
            if(response.status_code<210 and response.status_code>199):
                templates=json.loads(response.text)
                if r is not None and get_redis_status()=='ok':
                    r.delete('key_templates')
                    for t in templates:
                        print(t)
                        r.lpush('key_templates',json.dumps(t))
            else:
                return ['Unavailable']
        except Exception as e:
            print(f"An exception occurred in get_sidebar_templates: {e}")
            current_app.logger.error(f"An error occurred in get_sidebar_templates: {e} ")
            raise Exception("An error occurred during sidebar templates fetching") from e
        return templates
    
async def get_sidebar_compositions_ehrbase(auth,url_base):
    current_app.logger.debug('inside get_sidebar_compositions')
    async with httpx.AsyncClient() as client:
        r=current_app.config['REDIS_CLIENT']
        if r is not None:
            redistatus=get_redis_status()
            if redistatus=='ok' and r.exists('key_compositions') and r.llen('key_compositions')>0:
                #retrieve data from redis
                print('GGGGGGGGGGGGG')
                current_app.logger.debug('GGGGGGGGGG')
                compositions=r.lrange('key_compositions',0,-1)
                return compositions
        print('HHHHHHHHHHHHHH')
        current_app.logger.debug('HHHHHHHHHHHH')
        #retrieve data from EHRBase server
        compositions=[]
        try:
            #get compositions
            myurl=url_normalize(url_base  + '/query/aql')
            data={}
            aqltext="SELECT c/uid/value FROM EHR e CONTAINS COMPOSITION c"
            data['q']=aqltext
            response = await client.post(myurl,headers={'Authorization':auth,'Content-Type': 'application/json'}, data=json.dumps(data))
            compositions={}
            if(response.status_code<210 and response.status_code>199):
                comp_rows=json.loads(response.text)['rows']
                compositions=[c[0] for c in comp_rows]
                if r is not None and get_redis_status()=='ok':
                    r.delete('key_compositions')
                    r.lpush('key_compositions',*compositions)
            else:
                compositions=['Unavailable']
        except Exception as e:
            print(f"An exception occurred in get_sidebar_compositions while getting compositions in : {e}")
            current_app.logger.error(f"An error occurred in get_sidebar_compositions while getting compositions: {e} ")
            raise Exception("An error occurred during sidebar compositions fetching") from e
        return compositions

async def get_sidebar_queries_ehrbase(auth,url_base):
    current_app.logger.debug('inside get_sidebar_queries')
    async with httpx.AsyncClient() as client:
        r=current_app.config['REDIS_CLIENT']
        if r is not None:
            redistatus=get_redis_status()
            if redistatus=='ok' and r.exists('key_queries') and r.llen('key_queries')>0:
                #retrieve data from redis
                print('GGGGGGGGGGGGG')
                current_app.logger.debug('GGGGGGGGGG')
                queries=r.lrange('key_queries',0,-1)
                queries=[json.loads(q) for q in queries]
                print(f'queries: {queries}')
                return queries
        print('HHHHHHHHHHHHHH')
        current_app.logger.debug('HHHHHHHHHHHH')
        #retrieve data from EHRBase server
        queries=[]
        try:
            #get queries
            myurl=url_normalize(url_base  + '/definition/query/')
            response = await client.get(myurl, headers={'Authorization':auth,'Content-Type': 'application/json'}) 
            print(response.status_code)
            if(response.status_code<210 and response.status_code>199):
                queries=json.loads(response.text)['versions']
                if r is not None and get_redis_status()=='ok':
                    r.delete('key_queries')
                    for q in queries:
                        r.lpush('key_queries',json.dumps(q))
            else:
                return ['Unavailable']
        except Exception as e:
            print(f"An exception occurred in get_sidebar_queries: {e}")
            current_app.logger.error(f"An error occurred in get_sidebar_queries: {e} ")
            raise Exception("An error occurred during sidebar queries fetching") from e
        return queries

#EHR methods
async def get_ehr_by_ehrid_ehrbase(auth,url_base,ehrid):
    async with httpx.AsyncClient() as client:
        current_app.logger.debug('inside get_ehr_by_ehrid_ehrbase')
        print('inside get_ehr_by_ehrid_ehrbase')
        print(f'ehrid: {ehrid}')
        myresp={}
        try:
            #get ehr by ehrid
            myurl=url_normalize(url_base  + 'ehr/'+ehrid)
            print(f'auth: {auth}')
            print(f'myurl: {myurl}')
            print(f'ehrid: {ehrid}')
            print(f'client: {client}')
            response = await client.get(myurl, params={},headers={'Authorization':auth, 
                'Content-Type':'application/json','Accept': 'application/json','Prefer': 'return={representation|minimal}'},timeout=20000 )
    #         myresp['status']='success'
    #         myresp['ehr']=json.loads('''{"system_id":{
    #   "_type" : "HIER_OBJECT_ID",
    #   "value" : "local.ehrbase.org"
    # },"ehr_id":{
    #   "_type" : "HIER_OBJECT_ID",
    #   "value" : "56e46cce-d8c9-4db8-940b-ee3db170a646"
    # },"ehr_status":{"uid":{
    #   "_type" : "OBJECT_VERSION_ID",
    #   "value" : "775f39a4-edb1-4062-9607-91b7be57a0c5::local.ehrbase.org::1"
    # },"archetype_node_id":"openEHR-EHR-EHR_STATUS.generic.v1","name":{
    #   "_type" : "DV_TEXT",
    #   "value" : "EHR Status"
    # },"subject":{
    #   "_type" : "PARTY_SELF"
    # },"is_queryable":true,"is_modifiable":true,"_type":"EHR_STATUS"},"time_created":{
    #   "_type" : "DV_DATE_TIME",
    #   "value" : "2025-01-10T11:44:21.816885Z"
    # }}''')
            print(response.status_code)
            if 200 <= response.status_code < 210:
                myresp['status']="success"
                myresp["ehr"]=json.loads(response.text)
            else:
                myresp['status']='unavailable'
                myresp["ehr"]=json.loads(response.text)
        except Exception as e:
            print(f"An exception occurred in get_ehr_by_ehrid_ehrbase: {e}")
            current_app.logger.error(f"An error occurred in get_ehr_by_ehrid_ehrbase: {e} ")
            raise Exception("An error occurred during getting ehr by ehrid") from e  
        return myresp
