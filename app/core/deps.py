from fastapi import Depends, HTTPException, status, Request
from app.core.security import verify_token
from app.schemas.auth import JwtPayload

def get_token_from_cookie(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return token

def get_current_user(token: str = Depends(get_token_from_cookie)) -> JwtPayload:
    payload_dict = verify_token(token)
    if not payload_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return JwtPayload(**payload_dict)

class RequireRole:
    def __init__(self, required_role: str):
        self.required_role = required_role

    def __call__(self, user: JwtPayload = Depends(get_current_user)):
        if "admin" not in user.roles and self.required_role not in user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires {self.required_role} role",
            )
        return user

class RequirePermission:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(self, user: JwtPayload = Depends(get_current_user)):
        if "admin" not in user.roles and self.required_permission not in user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires '{self.required_permission}' permission",
            )
        return user
