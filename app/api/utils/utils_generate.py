# Run uvicorn app.main:app --reload

# generate.py
import json
import shutil
import os
import asyncio
import time
import logging
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, NoReturn, Optional

from ...database import db
from ...dependencies import get_current_user_id
from ...models import StartupRequest
from ...socket_config import manager
from metagpt.roles import (
    Architect,
    Engineer,
    ProductManager,
    ProjectManager,
    QaEngineer,
)
from metagpt.team import Team
from metagpt.config import CONFIG
from metagpt.const import DEFAULT_WORKSPACE_ROOT, BEACHHEAD_ROOT

logger = logging.getLogger(__name__)
router = APIRouter()

# Directory for user-specific code generation
USER_CODE_ROOT = Path("/path/to/user_generated_code")


async def startup(startup_request: StartupRequest):
    # # Configuration and team setup
    # if startup_request.project_name:
    #     CONFIG.project_name = startup_request.project_name
    # CONFIG.project_path = Path.cwd() / startup_request.project_name
    # CONFIG.inc = startup_request.inc
    # CONFIG.reqa_file = startup_request.reqa_file
    # CONFIG.max_auto_summarize_code = startup_request.max_auto_summarize_code
    print("Starting generation\n\n\n")

    #  # Use in the PrepareDocuments action according to Section 2.2.3.5.1 of RFC 135.
    # CONFIG.project_name = "beachhead"  # Setting project name to 'beachhead'
    # CONFIG.project_path = Path.cwd() / "beachhead"  # Setting project path to a 'beachhead' directory in the current working directory
    # if project_path:
    #     inc = True
    #     project_name = project_name or Path(project_path).name
    # CONFIG.project_name = project_name
    # CONFIG.inc = inc
    # CONFIG.reqa_file = reqa_file
    # CONFIG.max_auto_summarize_code = max_auto_summarize_code

    CONFIG.project_path = startup_request.project_path
    if startup_request.project_path:
        inc = True
        # project_name = project_name or Path(startup_request.project_path).name
        
    CONFIG.project_name = startup_request.project_name
    CONFIG.inc = startup_request.inc
    CONFIG.reqa_file = startup_request.reqa_file
    CONFIG.max_auto_summarize_code = startup_request.max_auto_summarize_code

    company = Team()
    company.hire([ProductManager(), Architect(), ProjectManager()])

    if startup_request.implement or startup_request.code_review:
        company.hire([Engineer(n_borg=5, use_code_review=startup_request.code_review)])

    if startup_request.run_tests:
        company.hire([QaEngineer()])

    company.invest(startup_request.investment)
    company.run_project(startup_request.idea)
    await company.run(n_round=startup_request.n_round)


def read_user_contents(user_path: Path):
    contents = {}
    for file_path in user_path.glob("**/*"):
        if file_path.is_file():
            with open(file_path, "r") as file:
                contents[str(file_path)] = file.read()
    return contents


def clear_user_contents(user_id: str):
    user_path = Path(BEACHHEAD_ROOT, user_id)
    if user_path.exists():
        shutil.rmtree(user_path)
        logger.info(f"User data for {user_id} has been cleaned up.")


# def clear_beachhead_contents():
#     beachhead_path = BEACHHEAD_ROOT
#     if beachhead_path.exists():
#         shutil.rmtree(beachhead_path)


async def background_generation_process(
    startup_request: StartupRequest, user_id: str, aisession_id: Optional[str] = None
):
    # user_path = USER_CODE_ROOT / user_id
    # user_path.mkdir(parents=True, exist_ok=True)

    # if aisession_id == None:
    #     aisession = await db["aisessions"].insert_one({"user_id": user_id, "status": "In Progress"})
    #     aisession_id = aisession.inserted_id

    # aisession = await db["aisessions"].find_one({"_id": aisession_id})

    await startup(startup_request)
    # code = read_user_contents(user_path)

    # Save the code and update the database
    # with open(user_path / 'code.json', 'w') as f:
    #     json.dump(code, f, indent=4)

    # await db["aisessions"].update_one(
    #     {"_id": aisession_id},
    #     {"$set": {"generated_data.code": code}},
    # )

    # await manager.send_update(user_id, aisession_id, {"aisession_id": aisession_id, "status": "Completed", "code": code})
    # clear_user_contents(user_path)
    pass


def secure_delete(path):
    if os.path.exists(path):
        shutil.rmtree(path)
        logger.info(f"Successfully deleted {path}")
    else:
        logger.error(f"Error while deleting {path}: Path does not exist")
