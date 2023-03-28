import uvicorn
from serve.internal import api

if __name__ == "__main__":
    uvicorn.run(api.app, port=5000)