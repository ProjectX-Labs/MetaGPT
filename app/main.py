import os
import logging
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import generate
from contextlib import asynccontextmanager

from .socket_config import sio, manager
from .database import connect_to_mongo, close_mongo_connection


# Database connection using lifespan event handlers
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server startup ")
    await connect_to_mongo()
    yield
    # Clean up the ML models and release the resources
    print("Server shutdown")
    await close_mongo_connection()


app = FastAPI(
    lifespan=lifespan,
    title="ProjectX x Metagpt",
    description="Generate code in minutes",
    version="0.1.0",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Support Team",
        "email": "info@projectxlabs.co",
    },
    servers=[{"url": "http://localhost:8001", "description": "Metagpt server"}],
)

app.mount("/", manager.get_app())

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router, prefix="/generate", tags=["generate"])


# Test route
@app.get("/")
async def root():
    return {"message": "Hello World"}


# If using terminal to run the server, use the following command:
#


# If running this file directly, start the server.
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("your_app_module:app", host="0.0.0.0", port=8000)
