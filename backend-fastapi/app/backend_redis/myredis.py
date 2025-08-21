import redis
import logging


def create_redis_client(redishostname, redisport):
    try:
        print(f"Connecting to redis server at {redishostname}:{redisport}")
        logging.info(f"Connecting to redis server at {redishostname}:{redisport}")
        r = redis.StrictRedis(
            host=redishostname, port=redisport, db=0, decode_responses=True
        )
        r.ping()
        logging.info("Connected to Redis server successfully")
        return r
    except Exception as e:
        logging.error(f"Error connecting to Redis server: {e}")
        print(f"Error in create_redis_client: {e}")
        return None


def get_redis_status(redis_client):
    try:
        redis_client.ping()
        return "ok"
    except:
        return "error"


def remove_item_from_redis_list(redis_client, listname, value, version=""):
    items = redis_client.lrange(listname, 0, -1)
    for item in items:
        if value in item and version in item:
            redis_client.lrem(listname, 1, item)
            return 1
    return 0
