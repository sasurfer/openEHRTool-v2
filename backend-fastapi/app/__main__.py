import uvicorn
from app.app_factory import create_app

if __name__ == "__main__":
    app=create_app()
    uvicorn.run("app.app_factory:create_app", host="127.0.0.1", port=5000, lifespan="on",reload=True)



