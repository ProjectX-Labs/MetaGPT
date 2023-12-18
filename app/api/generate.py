# generate.py
import os
import asyncio
import shutil
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from metagpt.roles import Architect, Engineer, ProductManager, ProjectManager, QaEngineer
from metagpt.team import Team
from metagpt.const import DEFAULT_WORKSPACE_ROOT
from metagpt.config import CONFIG

router = APIRouter()

class StartupRequest(BaseModel):
    idea: str
    investment: float = 3.0
    n_round: int = 5
    code_review: bool = False
    run_tests: bool = False
    implement: bool = True

async def startup(idea: str, investment: float, n_round: int, code_review: bool, run_tests: bool, implement: bool):
    CONFIG.project_name = "beachhead"
    company = Team()
    company.hire([ProductManager(), Architect(), ProjectManager()])

    if implement or code_review:
        company.hire([Engineer(n_borg=5, use_code_review=code_review)])

    if run_tests:
        company.hire([QaEngineer()])

    company.invest(investment)
    company.start_project(idea)
    await company.run(n_round=n_round)

def read_beachhead_contents():
    beachhead_path = DEFAULT_WORKSPACE_ROOT / "beachhead"
    contents = {}
    for file_path in beachhead_path.glob("**/*"):
        if file_path.is_file():
            with open(file_path, "r") as file:
                contents[str(file_path)] = file.read()
    return contents

@router.post("/")
async def generate(request: Request):
    try:
        body = await request.json()
        startup_request = StartupRequest(**body)
    except:
        with open("test_idea_files/input.txt", "r") as file:
            idea = file.read().strip()
        startup_request = StartupRequest(idea=idea)

    await startup(startup_request.idea, startup_request.investment, startup_request.n_round, startup_request.code_review, startup_request.run_tests, startup_request.implement)
    beachhead_contents = read_beachhead_contents()
    return {"message": "Startup process initiated successfully", "contents": beachhead_contents}

@router.get("/test")
async def generate_default():
    # return {"message": "Startup process initiated successfully with default input"}
    try:
        with open("test_idea_files/input.txt", "r") as file:
            idea = file.read().strip()
        startup_request = StartupRequest(idea=idea)

        await startup(startup_request.idea, startup_request.investment, startup_request.n_round, startup_request.code_review, startup_request.run_tests, startup_request.implement)
        beachhead_contents = read_beachhead_contents() 
        return {"message": "Startup process initiated successfully with default input", "contents": beachhead_contents }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
