# Run uvicorn app.main:app --reload

# generate.py
import shutil
import os
import asyncio
from typing import Any, Optional
from django import db
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from ..dependencies import get_current_user_id
from ..models import StartupRequest, GenerationRequest
from .utils.utils_generate import *

router = APIRouter()


@router.post("/{aisession_id}", operation_id="generate")
async def generate(
    aisession_id: str,
    generation_data: GenerationRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
):
    # print("Generation Request here: " + generation_data.idea)
    try:
        # Get user_id from middleware
        # combined_idea = (
        #     generation_data.idea + generation_data.app_details
        #     if generation_data.app_details is not None
        #     else ""
        # )
        generationRequest = StartupRequest(
            idea=generation_data.idea,
        )
        clear_beachhead_contents()
        # Add to background tasks
        background_tasks: BackgroundTasks
        background_tasks.add_task(
            background_generation_process,
            generationRequest,
            user_id,
            aisession_id,
        )
        return {"message": "Generation process initiated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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