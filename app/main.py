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
    servers=[{"url": "http://localhost:8000", "description": "Metagpt server"}],
)

app.mount("/ws", manager.get_app())


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


def get_client_id_by_sid(self, sid):
    for client_id, client_sid in self.active_connections.items():
        if client_sid == sid:
            return client_id
    return None


@sio.event
async def connect(sid, environ):
    user_id = environ[
        "HTTP_USER_ID"
    ]  # Assuming user_id is passed in the request headers
    aisession_id = environ.get("HTTP_AISESSION_ID")
    client_id = user_id + "_" + aisession_id

    manager.active_connections[client_id] = sid


# This event is triggered when a client disconnects
@sio.event
async def disconnect(sid):
    # Remove sid from active_connections

    client_id = get_client_id_by_sid(
        sid
    )  # Implement this function to map sid to user_id
    manager.active_connections.pop(client_id, None)


# # Custom event for receiving a message from the client
# @sio.event
# async def receive_message(sid, data):
#     # Here, 'data' is the message received from the client
#     print(f"Received message from {sid}: {data}")
#     # You can further process this data or send an update to the client or room


# If running this file directly, start the server.
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("your_app_module:app", host="0.0.0.0", port=8000)
