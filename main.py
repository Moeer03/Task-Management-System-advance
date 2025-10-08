from fastapi import FastAPI, Path, HTTPException, Query, Body, Response, status
from pydantic import BaseModel, Field
from typing import Optional
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from db_test import init_db, create_task_in_db, display_all_tasks, display_one_task_in_db, update_flag_in_db, delete_task_in_db, update_task_in_db, close_db
from helper import dict_from_row
from contextlib import asynccontextmanager

# Load variables from .env file
load_dotenv(".env")

DB_FILE = os.getenv("DB_FILE")

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    print("DB initialized")

    yield  # <-- app runs while we're here

    # Shutdown
    close_db()
    print("DB closed")

app = FastAPI(lifespan=lifespan)

# --- Model ---
class Task(BaseModel):
    id: Optional[int] = None
    title: str = Field(..., min_length=3)
    description: Optional[str] = None
    completion_flag: bool = Field(default=False)


# --- Routes ---
@app.post("/tasks/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: Task):
    task_id = create_task_in_db(task)

    created_task = {**task.model_dump(), "id": task_id}
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=created_task,
        headers={"Location": f"/tasks/{task_id}"}
    )


@app.get("/tasks/", response_model=list[Task], status_code=status.HTTP_200_OK)
def display_tasks(completed: Optional[bool] = Query(None)):
    rows = display_all_tasks(completed)

    return [dict_from_row(row) for row in rows]


@app.get("/tasks/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
def display_task(task_id: int = Path(gt=0)):
    row = display_one_task_in_db(task_id)

    if not row:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    return dict_from_row(row)

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(
    task_id: int = Path(gt=0),
    completion_flag: bool = Body(..., embed=True)
):
    
    row = update_flag_in_db(task_id, completion_flag)

    if not row:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    return dict_from_row(row)

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int = Path(gt=0)):
    
    changes = delete_task_in_db(task_id)
    
    if changes == 0:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.patch("/update_title/{task_id}", response_model=Task)
def update_task_partial(
    task_id: int = Path(gt=0),
    title: Optional[str] = Body(None, min_length=3),
    description: Optional[str] = Body(None)
):
    updated_row = update_task_in_db(task_id, title, description)
    
    if not updated_row:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    return dict_from_row(updated_row)