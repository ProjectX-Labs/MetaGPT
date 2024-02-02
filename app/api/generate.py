# generate.py
import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from app.dependencies import get_current_user_id
from app.models import GenerationRequest, StartupRequest
from .utils.utils_generate import startup, clear_user_contents, background_generation_process
from metagpt.const import DEFAULT_WORKSPACE_ROOT, BEACHHEAD_ROOT

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/generate-mvp", operation_id="generate_mvp")
async def generate_mvp(
    generation_data: GenerationRequest,
    background_tasks: BackgroundTasks, 
    user_id: str = Depends(get_current_user_id)
):
    try:
        generationRequest = StartupRequest(idea=generation_data.idea)
        

        background_tasks.add_task(
            background_generation_process,
            generationRequest, 
            user_id
        )
        return {
            "status": "success",
            "message": "Generation process started successfully"
        }
    except Exception as e:
        logger.error(f"Error during project generation for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Generation process failed")


# @router.post("/develop-project")
# async def develop_project( background_tasks: BackgroundTasks, user_id: str = Depends(get_current_user_id)):
#     pass
