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
