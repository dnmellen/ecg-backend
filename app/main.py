import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from app.api.routers.users import router as users_router
from app.api.routers.auth import router as auth_router
from app.api.routers.ecg import router as ecg_router
from app.config import settings
from app.models.database import sessionmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    stream=sys.stdout, level=logging.DEBUG if settings.debug_logs else logging.INFO
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()


app = FastAPI(lifespan=lifespan, title=settings.project_name, docs_url="/api/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(ecg_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)
