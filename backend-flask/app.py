from app import create_app
from app.config import Config
from app.client import client        
# import uvicorn


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
    #uvicorn.run("app:create_app", host="127.0.0.1", port=5000 ,reload=True)



