import redis
from .config import get_config
from flask import current_app

def get_redis_client():
    nodename,redishostname,redisport = get_config()
    try:
        print(f'Connecting to redis server at {redishostname}:{redisport}')
        r = redis.Redis(host=redishostname, port=redisport, db=0, decode_responses=True)
        r.ping()
        return r
    except Exception as e:
        print(f'Error in get_redis_client: {e}')
        return None


def get_redis_status():
    try:
        r=current_app.config['REDIS_CLIENT']
        r.ping()
        return 'ok'
    except:
        return 'error'
    