from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exception_handler import app_exception_handler
from app.core.exceptions import AppException
from app.db.session import is_db_connected

logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(message)s")

app = FastAPI(
    redirect_slashes=True,
    title="FastAPI Boilerplate",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials="*" not in settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)

app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logging.info("Starting up...")
    logging.info(f"DB Status: {await is_db_connected()}")

@app.get("/health")
async def get_health():
    return {"message": "Health OK"}