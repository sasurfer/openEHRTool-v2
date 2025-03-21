import datetime
import jwt
from fastapi import HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

# Create JWT token
def create_jwt_token(user_id: str, secret_key: str):
    expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=100000)
    token = jwt.encode({'user_id': user_id, 'exp': expiration_time}, secret_key, algorithm='HS256')
    return token

# Verify JWT token
def verify_jwt_token(token: str, secret_key: str):
    try:
        # Decode the JWT token
        decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
        return decoded  # Return decoded user data (e.g., user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Extract JWT from the Authorization header
def get_token_from_header(request: Request):
    tokeninauthheader = request.headers.get('Authorization')
    if not tokeninauthheader:
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = tokeninauthheader.split('Bearer ')[1]
    return token
