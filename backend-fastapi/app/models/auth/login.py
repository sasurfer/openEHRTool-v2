from pydantic import BaseModel, HttpUrl

# Define the structure of the request body
class LoginRequest(BaseModel):
    username: str
    password: str
    url: HttpUrl
