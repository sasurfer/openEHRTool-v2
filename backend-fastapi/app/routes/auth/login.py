from fastapi import FastAPI, APIRouter, HTTPException, Request, Depends
from app.utils import getauth, check_event_loop_status, setEHRbasepaths, insertlogline
from app.security import create_jwt_token, verify_jwt_token
import httpx
from app.backend_ehrbase.status.status import get_status
from app.models.auth.login import LoginRequest

router = APIRouter()

@router.post("/login")
async def login(request: Request,login_data: LoginRequest):
    logger = request.app.state.logger
    print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')

    username = login_data.username
    password = login_data.password
    input_url = login_data.url
    auth = getauth(username, password)

    try:
        url=str(input_url)+"rest/status"
        response = await get_status(request=request, auth=auth, url_status=url)
        if response.status_code == 200:
            ehrbase_version = response.json()['ehrbase_version']
            url_base, url_base_ecis, url_base_admin, url_base_management, url_base_status = setEHRbasepaths(str(input_url))
            request.app.state.url_base = url_base
            request.app.state.url_base_ecis = url_base_ecis
            request.app.state.url_base_admin = url_base_admin
            request.app.state.url_base_management = url_base_management
            request.app.state.url_base_status = url_base_status
            request.app.state.auth = auth
            request.app.state.ehrbase_version = ehrbase_version
            logger.debug(f"Successfully logged in with username: {username}")
            insertlogline(request.app.state.redis_client, f"Successfully logged in with username: {username} input_url: {input_url}")
            token = create_jwt_token(username,secret_key=request.app.state.secret_key)
            return {"token": token}
        else:
            insertlogline(request.app.state.redis_client, f"Unsuccessfully logged in with username: {username} input_url: {input_url}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        print(f"An exception occurred during login: {e}")
        raise HTTPException(status_code=500, detail="Server error during login")