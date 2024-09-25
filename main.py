from fastapi import FastAPI, Depends
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
from users import router as user_router
from tasks import router as task_router
from fastapi import HTTPException
import uvicorn

app = FastAPI()
slowapi_app = app
redis_client = redis.Redis(host="localhost", port=6379, db=0)
pg_username = "user"
pg_password = "password"
pg_database = "database"

engine = create_engine(
    f"postgresql://{pg_username}:{pg_password}@localhost/{pg_database}"
)
SQLModel.metadata.create_all(engine)


def jwt_required():
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                payload = jwt.decode(
                    kwargs.get("access_token"), "secret", algorithms=["HS256"]
                )
                kwargs["access_token"] = payload["user_id"]
                return await func(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                raise HTTPException(status_code=401, detail="Access token has expired")
            except jwt.InvalidTokenError:
                raise HTTPException(status_code=401, detail="Invalid access token")

        return wrapper

    return decorator


app.include_router(user_router)
app.include_router(task_router)

limiter = Limiter(key_func=get_remote_address)
app.include_limiter(limiter)

slowapi_app = FastAPI()
slowapi_app.state.slowapi_rate_limit = {"rate": "100/m", "block": True}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
