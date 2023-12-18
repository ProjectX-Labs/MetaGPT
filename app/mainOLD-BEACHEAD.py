import os
import asyncio
import logging
import shutil
from typing import Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.logger import logger as fastapi_logger
from jose import JWTError, jwt
from pydantic import BaseModel

# If metagpt is located in a subfolder, uncomment this with the correct path
# to add it to the Python path
# import sys
# sys.path.append('/path/to/metagpt')  # Replace with the actual path

from .database import connect_to_mongo, close_mongo_connection
from .core import config
from metagpt.roles import (
    Architect,
    Engineer,
    ProductManager,
    ProjectManager,
    QaEngineer,
)
from metagpt.team import Team
from metagpt.const import DEFAULT_WORKSPACE_ROOT
from metagpt.config import CONFIG
import asyncio
from pathlib import Path


# Database connection using lifespan event handlers 
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server startup ")
    await connect_to_mongo()
    yield
    # Clean up the ML models and release the resources
    print("Server shutdown")
    await close_mongo_connection()
    
# sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=[])
# manager = ConnectionManager(sio)  # Create an instance of ConnectionManager with the Socket.IO server

    
app = FastAPI(lifespan=lifespan,
              title="ProjectX x Metagpt",
    description="Generate code in minutes",
    version="0.1.0",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Support Team",
        
        "email": "info@projectxlabs.co",
    },
    servers=[{"url": "http://localhost:5000", "description": "Metagpt server"}],

)
# app.mount('/', manager.get_app())
# origins = [
#     "http://localhost:3000",  # The origin of your frontend
#     # Any origin - use wildcard *
    
    
# ]
origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request model
class StartupRequest(BaseModel):
    idea: str
    investment: float = 3.0
    n_round: int = 5
    code_review: bool = False
    run_tests: bool = False
    implement: bool = True

async def startup(
     idea: str = "...",  # Your innovative idea, such as 'Create a 2048 game.'
    investment: float = 3.0,  # Dollar amount to invest in the AI company.
    n_round: int = 5,  # Number of rounds for the simulation.
    code_review: bool = True,  # Whether to use code review.
    run_tests: bool = False,  # Whether to enable QA for adding & running tests.
    implement: bool = True,  # Enable or disable code implementation.
    project_name: str = "",  # Unique project name, such as 'game_2048'.
    inc: bool = False,  # Incremental mode. Use it to coop with existing repo.
    project_path: str = "",  # Specify the directory path of the old version project to fulfill the incremental requirements.
    reqa_file: str = "",  # Specify the source file name for rewriting the quality test code.
    max_auto_summarize_code: int = -1,  # The maximum number of times the 'SummarizeCode' action is automatically invoked, with -1 indicating unlimited. This parameter is used for debugging the workflow.
       
):
    from metagpt.roles import (
        Architect,
        Engineer,
        ProductManager,
        ProjectManager,
        QaEngineer,
    )
    from metagpt.team import Team

    # Use in the PrepareDocuments action according to Section 2.2.3.5.1 of RFC 135.
    CONFIG.project_path = project_path
    if project_path:
        inc = True
        project_name = project_name or Path(project_path).name
    CONFIG.project_name = project_name
    CONFIG.inc = inc
    CONFIG.reqa_file = reqa_file
    CONFIG.max_auto_summarize_code = max_auto_summarize_code

    company = Team()
    company.hire(
        [
            ProductManager(),
            Architect(),
            ProjectManager(),
        ]
    )

    if implement or code_review:
        company.hire([Engineer(n_borg=5, use_code_review=code_review)])

    if run_tests:
        company.hire([QaEngineer()])

    company.invest(investment)
    company.run_project(idea)
    asyncio.run(company.run(n_round=n_round))

def clear_beachhead():
    BEACHHEAD_PATH = DEFAULT_WORKSPACE_ROOT / "Beachhead"
    if BEACHHEAD_PATH.exists():
        shutil.rmtree(BEACHHEAD_PATH)
    BEACHHEAD_PATH.mkdir(parents=True, exist_ok=True)

def read_beachhead_contents():
    BEACHHEAD_PATH = DEFAULT_WORKSPACE_ROOT / "Beachhead"
    contents = {}
    for file_path in BEACHHEAD_PATH.glob("**/*"):
        if file_path.is_file():
            with open(file_path, "r") as file:
                contents[str(file_path)] = file.read()
    return contents

@app.post("/generate", operation_id="generate")
async def generate(request: Request):
    try:
        # Read request body if available or use default values
        try:
            body = await request.json()
            startup_request = StartupRequest(**body)
        except:
            with open("test_idea_files/input.txt", "r") as file:
                idea = file.read().strip()
            startup_request = StartupRequest(idea=idea)

        clear_beachhead()
        await startup(
            startup_request.idea,
            startup_request.investment,
            startup_request.n_round,
            startup_request.code_review,
            startup_request.run_tests,
            startup_request.implement,
        )
        beachhead_contents = read_beachhead_contents()
        return {"message": "Startup process initiated successfully", "contents": beachhead_contents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/", operation_id="generate_default")
async def generate_default():
    try:
        # Read the idea from the input.txt file
        with open("test_idea_files/input.txt", "r") as file:
            idea = file.read().strip()

        # Use default values for other parameters
        startup_request = StartupRequest(idea=idea)

        clear_beachhead()
        await startup(
            startup_request.idea,
            startup_request.investment,
            startup_request.n_round,
            startup_request.code_review,
            startup_request.run_tests,
            startup_request.implement,
        )
        beachhead_contents = read_beachhead_contents()
        return {"message": "Startup process initiated successfully with default input", "contents": beachhead_contents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
# # Uncomment to run using Uvicorn directly
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=5000)
