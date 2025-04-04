from fastapi import APIRouter, HTTPException, Request, Depends
from app.backend_ehrbase.dashboard.dashboard import get_dashboard_data_ehrbase
from app.security import verify_jwt_token, get_token_from_header
import httpx
from app.utils import get_logger

router = APIRouter()


@router.get("")
async def get_dashboard_data(
    request: Request, token: str = Depends(get_token_from_header)
):
    logger = get_logger(request)
    logger.debug("inside get_dashboard_data")
    auth = getattr(request.app.state, "auth", None)
    secret_key = getattr(request.app.state, "secret_key", None)
    if not auth or not verify_jwt_token(token, secret_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        url_base = request.app.state.url_base
        url_base_status = request.app.state.url_base_status
        url_base_management = request.app.state.url_base_management
        metrics, barData, pieData, info = await get_dashboard_data_ehrbase(
            request, auth, url_base, url_base_status, url_base_management
        )
        return {
            "dashboard_data": {
                "metrics": metrics,
                "barData": barData,
                "pieData": pieData,
                "info": info,
            }
        }

    except Exception as e:
        print(f"An exception occurred during get_dashboard_data: {e}")
        raise HTTPException(
            status_code=500, detail="Server error during get_dashboard_data"
        )
