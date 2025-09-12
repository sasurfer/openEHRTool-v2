from fastapi import FastAPI
from app.config import Config, get_config
from app.backend_redis.myredis import create_redis_client
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import httpx
from app.routes.auth.login import router as auth_router
from app.routes.home.dashboard import router as dashboard_router
from app.routes.sidebar.rsidebar.info import router as rsidebar_router
from app.routes.ehr.ehr import router as ehr_router
from app.routes.template.template import router as template_router
from app.routes.composition.composition import router as composition_router
from app.routes.contribution.contribution import router as contribution_router
from app.routes.query.query import router as query_router
from app.routes.admin.admin import router as admin_router
from app.routes.log.log import router as log_router


async def lifespan(app: FastAPI):
    # Initialize the HTTP client
    client = httpx.Client()
    app.state.httpx_client = client

    yield  # This keeps the app running until shutdown

    # Properly close the HTTP client on shutdown
    client.close()


def create_app():
    # Initialize FastAPI app
    app = FastAPI(lifespan=lifespan)

    # Enable CORS if needed
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Or specific origins
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
    )

    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("my_logger")
    app.state.logger = logger
    logger.debug("created app and added logger")

    # Add configuration to FastAPI's state
    # nodename, hostname, port, redishostname, redisport = get_config()
    nodename, redishostname, redisport = get_config()
    app.state.nodename = nodename
    # app.state.hostname = hostname
    # app.state.port = port
    app.state.redishostname = redishostname
    app.state.redisport = redisport

    # Add Redis client to FastAPI's state
    app.state.secret_key = Config.SECRET_KEY
    app.state.redis_client = create_redis_client(
        app.state.redishostname, app.state.redisport
    )

    # Load routes
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
    app.include_router(rsidebar_router, prefix="/rsidebar", tags=["rsidebar"])
    app.include_router(ehr_router, prefix="/ehr", tags=["ehr"])
    app.include_router(template_router, prefix="/template", tags=["template"])
    app.include_router(composition_router, prefix="/composition", tags=["composition"])
    app.include_router(
        contribution_router, prefix="/contribution", tags=["contribution"]
    )
    app.include_router(query_router, prefix="/query", tags=["query"])
    app.include_router(admin_router, prefix="/admin", tags=["admin"])
    app.include_router(log_router, prefix="/log", tags=["log"])

    return app
