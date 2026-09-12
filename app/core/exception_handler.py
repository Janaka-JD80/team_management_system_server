from fastapi.responses import JSONResponse
from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import AppException
import traceback

async def app_exception_handler(req: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": False, "message": exc.message, "data": None}
    )

async def http_exception_handler(req: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": False, "message": exc.detail, "data": None}
    )

async def validation_exception_handler(req: Request, exc: RequestValidationError):
    errors = exc.errors()
    return JSONResponse(
        status_code=422,
        content={"status": False, "message": "Validation Error", "data": errors}
    )

async def global_exception_handler(req: Request, exc: Exception):
    print(f"Unhandled Exception: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"status": False, "message": "Internal Server Error", "data": None}
    )