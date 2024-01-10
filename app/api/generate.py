# Run uvicorn app.main:app --reload

# generate.py
import shutil
import os
import asyncio
from typing import Any, Optional
from django import db
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from ..dependencies import get_current_user_id
from ..models import StartupRequest
from .utils.utils_generate import *

router = APIRouter()


@router.post("/{}", operation_id="generate")
async def generate(
    request: Request,
    aisession_id: str,
    idea: str,
    background_tasks: BackgroundTasks,
    app_details: Optional[Any] = None,
    user_id: str = Depends(get_current_user_id),
):
    print("Bingbadaboom Generating", user_id)
    print(request)
    try:
        print(idea)
        generationRequest = StartupRequest(
            idea=idea + app_details,
        )
        print("Generation Request here: " + generationRequest)
        clear_beachhead_contents()
        # Add to background tasks
        # background_tasks: BackgroundTasks
        # background_tasks.add_task(
        #     background_generation_process,
        #     generationRequest,
        #     user_id,
        #     aisession_id,
        # )
        return {"message": "Generation process initiated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
