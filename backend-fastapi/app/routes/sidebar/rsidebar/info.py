from fastapi import APIRouter, HTTPException, Request, Depends
from app.backend_ehrbase.sidebar.rsidebar.rsidebar import get_sidebar_ehrs_ehrbase, get_sidebar_templates_ehrbase, get_sidebar_compositions_ehrbase, get_sidebar_queries_ehrbase
from app.security import verify_jwt_token,get_token_from_header
from app.utils import get_logger
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/ehrs")
async def get_sidebar_ehrs(request: Request, token: str = Depends(get_token_from_header)):
    logger = get_logger(request)
    logger.debug('inside get_sidebar_ehrs')
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        url_base = request.app.state.url_base
        ehrs = await get_sidebar_ehrs_ehrbase(request,auth, url_base)
        return JSONResponse(content= {"ehrs": ehrs}, status_code=200)
    except Exception as e:
        print(f"An exception occurred during get_sidebar_ehrs: {e}")
        raise HTTPException(status_code=500, detail="Server error during get_sidebar_ehrs")

@router.get("/templates")
async def get_sidebar_templates(request: Request, token: str = Depends(get_token_from_header)):
    logger = get_logger(request)
    logger.debug('inside get_sidebar_templates')
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        url_base = request.app.state.url_base
        templates = await get_sidebar_templates_ehrbase(request,auth, url_base)
        return JSONResponse(content= {"templates": templates}, status_code=200)
    except Exception as e:
        print(f"An exception occurred during get_sidebar_templates: {e}")
        raise HTTPException(status_code=500, detail="Server error during get_sidebar_templates")

@router.get("/compositions")
async def get_sidebar_compositions(request: Request, token: str = Depends(get_token_from_header)):
    logger = get_logger(request)
    logger.debug('inside get_sidebar_compositions')
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        url_base = request.app.state.url_base
        compositions = await get_sidebar_compositions_ehrbase(request,auth, url_base)
        return JSONResponse(content= {"compositions": compositions}, status_code=200)
    except Exception as e:
        print(f"An exception occurred during get_sidebar_compositions: {e}")
        raise HTTPException(status_code=500, detail="Server error during get_sidebar_compositions")

@router.get("/queries")
async def get_sidebar_queries(request: Request, token: str = Depends(get_token_from_header)):
    logger = get_logger(request)
    logger.debug('inside get_sidebar_queries')
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        url_base = request.app.state.url_base
        queries = await get_sidebar_queries_ehrbase(request,auth, url_base)
        return JSONResponse(content= {"queries": queries}, status_code=200)
    except Exception as e:
        print(f"An exception occurred during get_sidebar_queries: {e}")
        raise HTTPException(status_code=500, detail="Server error during get_sidebar_queries")