# Run uvicorn app.main:app --reload

# generate.py
import shutil
import os
import asyncio
import subprocess
import logging
from typing import Any, Optional
from django import db
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from ..dependencies import get_current_user_id
from ..models import StartupRequest, GenerationRequest
from .utils.utils_generate import *

logger = logging.getLogger(__name__)
router = APIRouter()


def cleanup_container(container_name):
    subprocess.run(["docker", "rm", "-f", container_name])

@router.post("/{user_id}/generate")
async def generate_project(user_id: str, background_tasks: BackgroundTasks):
    try:
        container_name = f"projectx_gen_{user_id}"
        host_path = f"/path/to/user_data/{user_id}"
        container_path = "/app/data"

        cmd = [
            "docker", "run", "--name", container_name,
            "-v", f"{host_path}:{container_path}",
            "projectx_generation"
        ]
        subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        background_tasks.add_task(cleanup_container, container_name)
        return {"message": "Generation started"}
    except Exception as e:
        logger.error(f"Error during project generation for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Generation process failed")

@router.get("/get-files")
async def get_files():
    folder_path = "beachhead"
    file_contents = {}

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, folder_path)
            with open(file_path, 'r') as file:
                file_contents[relative_path] = file.read()

    return file_contents