import os
import asyncio
import logging
import shutil
from typing import Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
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
from .models import (
    Webhook,
    Branch,
    Commit,
    Action,
    Message,
    Question,
    ConsultScaffold,
    Task,
    ChatRequest,
    Conversation,
    AISession,
    Repository,
    RateLimit,
    User,
)
from .dependencies import get_current_user_id
from metagpt.roles import (
    Architect,
    Engineer,
    ProductManager,
    ProjectManager,
    QaEngineer,
)
from metagpt.team import Team
from metagpt.const import WORKSPACE_ROOT

app = FastAPI()

# Define request model
class StartupRequest(BaseModel):
    idea: str
    investment: float = 3.0
    n_round: int = 5
    code_review: bool = False
    run_tests: bool = False
    implement: bool = True

async def startup(
    idea: str,
    investment: float,
    n_round: int,
    code_review: bool,
    run_tests: bool,
    implement: bool,
):
    company = Team()
    company.hire([ProductManager(), Architect(), ProjectManager()])

    if implement or code_review:
        company.hire([Engineer(n_borg=5, use_code_review=code_review)])

    if run_tests:
        company.hire([QaEngineer()])

    company.invest(investment)
    company.start_project(idea)
    await company.run(n_round=n_round)

def clear_beachhead():
    BEACHHEAD_PATH = WORKSPACE_ROOT / "Beachhead"

    # Clear the contents if the folder exists, else create it
    if BEACHHEAD_PATH.exists():
        shutil.rmtree(BEACHHEAD_PATH)
    BEACHHEAD_PATH.mkdir(parents=True, exist_ok=True)

@app.post("/generate", operation_id="generate")
async def generate(
    request: StartupRequest, user_id: str = Depends(get_current_user_id)
):
    try:
        clear_beachhead()
        await startup(
            request.idea,
            request.investment,
            request.n_round,
            request.code_review,
            request.run_tests,
            request.implement,
        )
        return {"message": "Startup process initiated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Uncomment to run using Uvicorn directly
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
