from flask import Flask
from .client import client  # Importing the client function here to avoid circular imports
from .routes import load_routes  # Import the function that will load routes
from .config import Config
from flask_cors import CORS
from .myredis import get_redis_client
import os
import logging


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.app_context()
    # app.config.from_object('config')
    app.config['DEBUG'] = True
    app.config['PROPAGATE_EXCEPTIONS'] = True

    app.logger.info(f"Running with APP_ENV={os.getenv('APP_ENV')}")
    app.logger.info(f"Running with FLASK_ENV={os.getenv('FLASK_ENV')}")
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['HTTPX_CLIENT']=client
    app.config['REDIS_CLIENT']=get_redis_client()
    app.logger.debug('test debug')

    load_routes(app)
    return app


