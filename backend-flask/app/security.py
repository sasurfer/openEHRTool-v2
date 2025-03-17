import datetime
import jwt
from flask import current_app

def create_jwt_token(user_id):
    expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=100000)
    token = jwt.encode({'user_id': user_id, 'exp': expiration_time}, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def verify_jwt_token(token):
    try:
        # Decode the JWT token
        decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return decoded  # Return decoded user data (e.g., user_id)
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token

