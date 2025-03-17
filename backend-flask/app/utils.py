import base64
from .myredis import get_redis_status
from datetime import datetime
from flask import current_app
import asyncio

def getauth(username,password):
    message=username+":"+password
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    auth="Basic "+base64_message
    return auth

def setEHRbasepaths(input_url):
    '''set base paths for EHRBase'''
    url_base            = input_url + "rest/openehr/v1/"
    url_base_ecis       = input_url + "rest/ecis/v1/"
    url_base_admin      = input_url + "rest/admin/"
    url_base_management = input_url + "management/"
    url_base_status     = input_url + "rest/status"
    return url_base,url_base_ecis,url_base_admin,url_base_management,url_base_status

def insertlogline(line):
    if get_redis_status=='ok':
        r=current_app.config['REDIS_CLIENT']
        now = datetime.now()
        timestamp = now.strftime("%Y/%m/%d-%H:%M:%S-")
        mykey='log'
        try:
            r.rpush(mykey,timestamp+line)
        except Exception as e:
            return 'error:',e
    else:
        return 'error: redis not initialized'

def check_event_loop_status():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        print("ok")
    else:
        print("Event loop is not running.")