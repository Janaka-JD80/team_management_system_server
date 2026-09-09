from fastapi.responses import JSONResponse
from fastapi import Request

from app.core.exceptions import AppException

async def app_exception_handler(req: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status":False,
            "message":exc.message
        }
    )