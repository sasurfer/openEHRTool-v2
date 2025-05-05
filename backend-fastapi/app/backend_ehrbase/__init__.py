import datetime
import json
import httpx
from url_normalize import url_normalize
from app.backend_redis.myredis import get_redis_status
from fastapi import HTTPException


# Helper function to make GET requests
async def fetch_get_data(
    client: httpx.AsyncClient,
    url: str,
    headers: dict,
    params: dict = None,
    timeout: int = None,
):
    try:
        response = await client.get(
            url, headers=headers, params=params, timeout=timeout
        )
        response.raise_for_status()  # Raise an exception for 4xx/5xx responses
        return response
    except httpx.HTTPStatusError as e:
        if 400 <= e.response.status_code < 500:
            try:
                error_details = e.response.json()
            except ValueError:
                error_details = e.response.text or "No content in response"
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"HTTP Error: {error_details}",
            )
            raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")


# Helper function to make POST requests
async def fetch_post_data(
    client: httpx.AsyncClient,
    url: str,
    headers: dict,
    data: str = None,
    params: dict = None,
    timeout: int = None,
):
    try:
        # Include data in the body and params in the query string if provided
        response = await client.post(
            url, headers=headers, data=data, params=params, timeout=timeout
        )
        response.raise_for_status()  # Raise an exception for 4xx/5xx responses
        return response
    except httpx.HTTPStatusError as e:
        if 400 <= e.response.status_code < 500:
            try:
                error_details = e.response.json()
            except ValueError:
                error_details = e.response.text or "No content in response"
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"HTTP Error: {error_details}",
            )
        else:
            raise HTTPException(status_code=500, detail=f"Error posting data: {e}")


async def fetch_put_data(
    client: httpx.AsyncClient,
    url: str,
    headers: dict,
    data: str = None,
    params: dict = None,
    timeout: int = None,
):
    try:
        # Include data in the body and params in the query string if provided
        response = await client.put(
            url, headers=headers, data=data, params=params, timeout=timeout
        )
        response.raise_for_status()  # Raise an exception for 4xx/5xx responses
        return response
    except httpx.HTTPStatusError as e:
        if 400 <= e.response.status_code < 500:
            try:
                error_details = e.response.json()
            except ValueError:
                error_details = e.response.text or "No content in response"
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"HTTP Error: {error_details}",
            )
        else:
            raise HTTPException(status_code=500, detail=f"Error putting data: {e}")


async def fetch_delete_data(
    client: httpx.AsyncClient,
    url: str,
    headers: dict,
    params: dict = None,
    timeout: int = None,
):
    try:
        # Use the params in the query string if provided
        response = await client.delete(
            url, headers=headers, params=params, timeout=timeout
        )
        response.raise_for_status()  # Raise an exception for 4xx/5xx responses
        return response
    except httpx.HTTPStatusError as e:
        if 400 <= e.response.status_code < 500:
            try:
                error_details = e.response.json()
            except ValueError:
                error_details = e.response.text or "No content in response"
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"HTTP Error: {error_details}",
            )
        else:
            raise HTTPException(status_code=500, detail=f"Error deleting data: {e}")
