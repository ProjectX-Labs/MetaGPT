# generate.py
import shutil
import os
import asyncio
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
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

router = APIRouter()


class StartupRequest(BaseModel):
    idea: str
    investment: float = 3.0
    n_round: int = 5
    code_review: bool = True
    run_tests: bool = False
    implement: bool = True
    project_name: str = "beachhead"
    inc: bool = False
    project_path: str = ""
    reqa_file: str = ""
    max_auto_summarize_code: int = -1


async def startup(startup_request: StartupRequest):
    CONFIG.project_name = startup_request.project_name
    CONFIG.project_path = Path.cwd() / startup_request.project_name
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
    # asyncio.run(company.run(n_round=3))
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


@router.get("/")
async def generate(aisession_id: str, idea: str, app_details: any):
    try:
        generationRequest = StartupRequest(
            idea=idea + app_details,
        )
        clear_beachhead_contents()  # Clear existing contents before starting
        await startup(generationRequest)
        beachhead_contents = read_beachhead_contents()  # Read new contents
        return {
            "message": "Startup process initiated successfully",
            "contents": beachhead_contents,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test")
async def generate_default():
    try:
        with open(test_file_path, "r") as file:
            idea = file.read().strip()
        startup_request = StartupRequest(idea=idea)
        clear_beachhead_contents()  # Clear existing contents before starting
        await startup(startup_request)
        beachhead_contents = read_beachhead_contents()  # Read new contents
        return {
            "message": "Startup process initiated successfully with default input",
            "contents": beachhead_contents,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
