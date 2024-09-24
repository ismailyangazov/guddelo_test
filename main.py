from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import jwt
import redis
from sqlmodel import Session, SQLModel, Field
from sqlalchemy import create_engine
from slowapi import Limiter, _rate_limited
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI()
slowapi_app = app
redis_client = redis.Redis(host='localhost', port=6379, db=0)
pg_username = 'user'
pg_password = 'password'
pg_database = 'database'

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    password: str

engine = create_engine(f"postgresql://{pg_username}:{pg_password}@localhost/{pg_database}")
SQLModel.metadata.create_all(engine)

def jwt_required():
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                payload = jwt.decode(kwargs.get("access_token"), "secret", algorithms=["HS256"])
                kwargs["access_token"] = payload["user_id"]
                return await func(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                raise HTTPException(status_code=401, detail="Access token has expired")
            except jwt.InvalidTokenError:
                raise HTTPException(status_code=401, detail="Invalid access token")
        return wrapper
    return decorator

class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    description: Optional[str]
    user_id: int

class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/register", rate=(100, 60))
async def register(request: RegisterRequest):
    new_user = User(username=request.username, password=request.password)
    with Session(engine) as session:
        session.add(new_user)
        await session.commit()
        return {"message": "User created successfully"}

class Token(BaseModel):
    access_token: str

@app.post("/login", rate=(100, 60))
async def login(request: LoginRequest):
    user = (await Session(engine).exec(select(User).where(User.username == request.username))).first()
    if not user or user.password != request.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = jwt.encode({"user_id": user.id}, "secret", algorithm="HS256")
    return {"access_token": token}

class LogoutRequest(BaseModel):
    access_token: str

@app.post("/logout", rate=(100, 60))
async def logout(request: LogoutRequest):
    try:
        payload = jwt.decode(request.access_token, "secret", algorithms=["HS256"])
        with Session(engine) as session:
            await session.exec(
                Task.update().where(Task.user_id == payload["user_id"]).delete())
            return {"message": "User logged out successfully"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")

class TaskRequest(BaseModel):
    title: str
    description: Optional[str]
    user_id: int

limiter = Limiter(key_func=get_remote_address)
app.include_router(slowapi_app)

@app.post("/tasks", rate=(100, 60))
@_rate_limited(limiter)
async def create_task(request: TaskRequest, access_token: str = Depends(jwt_required)):
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

@app.get("/tasks", rate=(100, 60))
@_rate_limited(limiter)
async def get_tasks(access_token: str = Depends(jwt_required)):
    try:
        payload = jwt.decode(access_token, "secret", algorithms=["HS256"])
        with Session(engine) as session:
            tasks = (await session.exec(select(Task).where(Task.user_id == payload["user_id"]))).all()
            return {"tasks": [{"title": task.title, "description": task.description} for task in tasks]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")

class GetTaskResponse(BaseModel):
    task: dict

@app.get("/tasks/{task_id}", rate=(100, 60))
@_rate_limited(limiter)
async def get_task(task_id: int, access_token: str = Depends(jwt_required)):
    try:
        payload = jwt.decode(access_token, "secret", algorithms=["HS256"])
        with Session(engine) as session:
            task = (await session.exec(select(Task).where(Task.id == task_id))).first()
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

@app.put("/tasks/{task_id}")
@_rate_limited(limiter, rate=(100, 60))
async def update_task(task_id: int, request: UpdateTaskRequest, access_token: str = Depends(jwt_required)):
    try:
        payload = jwt.decode(access_token, "secret", algorithms=["HS256"])
        with Session(engine) as session:
            task = (await session.exec(select(Task).where(Task.id == task_id))).first()
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

@app.delete("/tasks/{task_id}", rate=(100, 60))
@_rate_limited(limiter)
async def delete_task(task_id: int, access_token: str = Depends(jwt_required)):
    try:
        payload = jwt.decode(access_token, "secret", algorithms=["HS256"])
        with Session(engine) as session:
            task = (await session.exec(select(Task).where(Task.id == task_id))).first()
            if not task or task.user_id != payload["user_id"]:
                raise HTTPException(status_code=404, detail="Task not found")
            await session.delete(task)
            await session.commit()
            return {"message": "Task deleted successfully"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")





