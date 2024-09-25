from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel
from typing import Optional
import jwt
from sqlmodel import Session, SQLModel, Field
from main import engine, jwt_required
import asyncio

class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    description: Optional[str]
    user_id: int

router = APIRouter()

@router.post("/tasks")
async def create_task(request: BaseModel, access_token: str = Depends(jwt_required)):
    try:
        payload = jwt.decode(access_token, "secret", algorithms=["HS256"])
        with Session(engine) as session:
            new_task = Task(title=request.title, description=request.description, user_id=payload["user_id"])
            await session.add(new_task)
            await session.commit()
            return {"message": "Task created successfully"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")

class GetTasksResponse(BaseModel):
    tasks: list[dict]

@router.get("/tasks")
async def get_tasks(access_token: str = Depends(jwt_required)):
    try:
        payload = jwt.decode(access_token, "secret", algorithms=["HS256"])
        with Session(engine) as session:
            tasks = (await session.exec(Task.select().where(Task.user_id == payload["user_id"]))).all()
            return {"tasks": [{"title": task.title, "description": task.description} for task in tasks]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")

class GetTaskResponse(BaseModel):
    task: dict

@router.get("/tasks/{task_id}")
async def get_task(task_id: int, access_token: str = Depends(jwt_required)):
    try:
        payload = jwt.decode(access_token, "secret", algorithms=["HS256"])
        with Session(engine) as session:
            task = (await session.exec(Task.select().where(Task.id == task_id))).first()
            if not task or task.user_id != payload["user_id"]:
                raise HTTPException(status_code=404, detail="Task not found")
            return {"task": {"title": task.title, "description": task.description}}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")

class UpdateTaskRequest(BaseModel):
    title: str
    description: Optional[str]

@router.put("/tasks/{task_id}")
async def update_task(task_id: int, request: UpdateTaskRequest, access_token: str = Depends(jwt_required)):
    try:
        payload = jwt.decode(access_token, "secret", algorithms=["HS256"])
        with Session(engine) as session:
            task = (await session.exec(Task.select().where(Task.id == task_id))).first()
            if not task or task.user_id != payload["user_id"]:
                raise HTTPException(status_code=404, detail="Task not found")
            task.title = request.title
            task.description = request.description
            await session.commit()
            return {"message": "Task updated successfully"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")

class DeleteTaskRequest(BaseModel):
    task_id: int

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, access_token: str = Depends(jwt_required)):
    try:
        payload = jwt.decode(access_token, "secret", algorithms=["HS256"])
        with Session(engine) as session:
            task = (await session.exec(Task.select().where(Task.id == task_id))).first()
            if not task or task.user_id != payload["user_id"]:
                raise HTTPException(status_code=404, detail="Task not found")
            await session.delete(task)
            await session.commit()
            return {"message": "Task deleted successfully"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")

