import os

from pprint import pprint

from fastapi import FastAPI as FastAPIOffline
import uvicorn
from backend.video.routers import router as router_video
from backend.video.routers import router_v2 as router_video2
from fastapi import Response

app = FastAPIOffline()


@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = Response()

    if request.method == "OPTIONS":
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    response = await call_next(request)

    response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

    return response


app.include_router(router_video)
app.include_router(router_video2)





@app.get("/")
async def root():
    return {"message": "Hello World"}


pprint(os.environ)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)