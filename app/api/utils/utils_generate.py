# Run uvicorn app.main:app --reload

# generate.py
import json
import shutil
import os
import asyncio
import time
from typing import Any, NoReturn

from ...database import db
import requests
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
from metagpt.roles import (
    Architect,
    Engineer,
    ProductManager,
    ProjectManager,
    QaEngineer,
)
from metagpt.team import Team
from metagpt.config import CONFIG
from metagpt.const import DEFAULT_WORKSPACE_ROOT
from ...dependencies import get_current_user_id
from ...models import StartupRequest
from ...socket_config import sio, manager

from ...socket_config import manager

router = APIRouter()


async def startup(startup_request: StartupRequest):
    CONFIG.project_name = startup_request.project_name
    CONFIG.project_path = Path.cwd() / startup_request.project_name
    CONFIG.inc = startup_request.inc
    CONFIG.reqa_file = startup_request.reqa_file
    CONFIG.max_auto_summarize_code = startup_request.max_auto_summarize_code

    company = Team()
    company.hire([ProductManager(), Architect(), ProjectManager()])

    print(startup_request.__str__)

    if startup_request.implement or startup_request.code_review:
        company.hire([Engineer(n_borg=5, use_code_review=startup_request.code_review)])

    if startup_request.run_tests:
        company.hire([QaEngineer()])

    company.invest(startup_request.investment)
    print("Startup Idea (Monkey)", startup_request.idea)
    time.sleep(3)

    company.run_project(startup_request.idea)

    await company.run(n_round=startup_request.n_round)


def read_beachhead_contents():
    beachhead_path = DEFAULT_WORKSPACE_ROOT / "beachhead"
    contents = {}
    for file_path in beachhead_path.glob("**/*"):
        if file_path.is_file():
            with open(file_path, "r") as file:
                contents[str(file_path)] = file.read()
    return contents


def clear_beachhead_contents():
    beachhead_path = DEFAULT_WORKSPACE_ROOT / "beachhead"
    if beachhead_path.exists():
        shutil.rmtree(beachhead_path)


# Get the directory of the current script
current_script_dir = os.path.dirname(os.path.abspath(__file__))
print(current_script_dir)
# Construct the path to the target file
test_file_path = os.path.join(current_script_dir, "../test_idea_files/input.txt")
print(test_file_path)


async def background_generation_process(
    startup_request: StartupRequest, user_id: str, aisession_id: str
):
    await startup(startup_request)
    code = read_beachhead_contents()
    print(code)

    # Save the code into a JSON file
    with open('chaching.json', 'w') as f:
        json.dump(code, f, indent=4)

    # Update the database record for the AI session
    process_results = await db["aisessions"].update_one(
        {"_id": aisession_id},  # Assuming aisession_id is the _id in MongoDB
        {"$set": {"generated_data.code": code}},
    )

    message = {
        "aisession_id": aisession_id,
        "status": "Completed",
        "code": code,
    }
    print(message)

    # Send a socket notification
    await manager.send_update(user_id, aisession_id, message)
