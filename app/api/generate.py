# generate.py
import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.dependencies import get_current_user_id
from app.models import GenerationRequest, StartupRequest
from .utils.utils_generate import (
    startup,
    clear_user_contents,
    background_generation_process,
)
from metagpt.const import DEFAULT_WORKSPACE_ROOT, BEACHHEAD_ROOT

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate-mvp", operation_id="generate_mvp")
async def generate_mvp(
    generation_data: GenerationRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
):
    try:
        # Combine the data into one string
        combined_idea_parts = [
            generation_data.projectName or "",
            generation_data.idea,
            generation_data.appType,
            ", ".join(generation_data.technology),
            generation_data.additionalDetails or "",
        ]
        combined_idea = " | ".join(
            filter(None, combined_idea_parts)
        )  # Filters out empty strings
        
        
        print(combined_idea)
        # generationRequest = StartupRequest(idea=combined_idea)

        # background_tasks.add_task(
        #     background_generation_process, generationRequest, user_id
        # )
        # Return a standardized JSON response with a status code
        return JSONResponse(
            status_code=202,  # 202 Accepted is often used for async operations
            content={
                "status": "successful",
                "message": "Generation process started successfully",
            }
        )
    except Exception as e:
        logger.error(f"Error during project generation for user {user_id}: {e}")
        return JSONResponse(
            status_code=500,  # Internal Server Error
            content={
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }
        )


# @router.post("/develop-project")
# async def develop_project( background_tasks: BackgroundTasks, user_id: str = Depends(get_current_user_id)):
#     pass
