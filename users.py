from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import jwt
from sqlmodel import Session, SQLModel, Field
from main import engine
import asyncio

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    password: str

router = APIRouter()

@router.post("/register")
async def register(request: BaseModel):
    new_user = User(username=request.username, password=request.password)
    with Session(engine) as session:
        session.add(new_user)
        await session.commit()
        return {"message": "User created successfully"}

class Token(BaseModel):
    access_token: str

@router.post("/login")
async def login(request: BaseModel):
    user = (await Session(engine).execute(
        User.select().where(User.username == request.username))).first()
    if not user or user.password != request.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = jwt.encode({"user_id": user.id}, "secret", algorithm="HS256")
    return {"access_token": token}

@router.post("/logout")
async def logout(request: Token):
    try:
        payload = jwt.decode(request.access_token, "secret", algorithms=["HS256"])
        with Session(engine) as session:
            await session.execute(
                User.update().where(User.id == payload["user_id"]).delete())
            return {"message": "User logged out successfully"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")

