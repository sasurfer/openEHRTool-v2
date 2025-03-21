import redis
from app.config import get_config

def create_redis_client():
    nodename,redishostname,redisport = get_config()
    try:
        print(f'Connecting to redis server at {redishostname}:{redisport}')
        r = redis.StrictRedis(host=redishostname, port=redisport, db=0, decode_responses=True)
        r.ping()
        return r
    except Exception as e:
        print(f'Error in create_redis_client: {e}')
        return None


def get_redis_status(redis_client):
    try:
        redis_client.ping()
        return 'ok'
    except:
        return 'error'


    