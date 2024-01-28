# Modified generate.py
import subprocess
import logging
import os
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.dependencies import get_current_user_id
from app.models import GenerationRequest
from .utils.utils_generate import (
    clear_user_contents,
    startup,
    clear_beachhead_contents,
    background_generation_process,
)
from metagpt.const import DEFAULT_WORKSPACE_ROOT, BEACHHEAD_ROOT

logger = logging.getLogger(__name__)
router = APIRouter()


def cleanup_container(container_name):
    try:
        subprocess.run(["docker", "rm", "-f", container_name], check=True)
        logger.info(f"Successfully cleaned up container {container_name}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to clean up container {container_name}: {e}")


@router.post("/generate-mvp", operation_id="generate_mvp")
async def generate_mvp(
    generation_data: GenerationRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
):
    try:
        container_name = f"projectx_gen_{user_id}"
        host_path = os.path.join(BEACHHEAD_ROOT, user_id)
        container_path = "/app/data"

        # Start the Docker container
        cmd = [
            "docker",
            "run",
            "--name",
            container_name,
            "-v",
            f"{host_path}:{container_path}",
            "projectx_generation",
        ]
        subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Clear previous data and start the generation process
        clear_user_contents(user_id)

        background_tasks.add_task(
            background_generation_process,
            generation_data,
            user_id,
            container_name,  # Pass the container name for further process
        )

        background_tasks.add_task(cleanup_container, container_name)
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Generation process started successfully",
            },
        )
    except Exception as e:
        logger.error(f"Error during project generation for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Generation process failed")


# @router.post("/develop-project")
# async def develop_project( background_tasks: BackgroundTasks, user_id: str = Depends(get_current_user_id)):
#     pass
