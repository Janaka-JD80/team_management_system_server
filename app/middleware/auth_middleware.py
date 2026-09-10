from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.security import verify_token
from app.schemas.auth import JwtPayload

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.cookies.get("access_token")
        
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        request.state.user = None
        
        if token:
            payload = verify_token(token)
            if payload:
                request.state.user = JwtPayload(**payload)
        
        response = await call_next(request)
        return response
