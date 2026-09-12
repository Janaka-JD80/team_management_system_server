from typing import List, Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID

class JwtPayload(BaseModel):
    sub: str
    user_id: Optional[str] = None
    exp: int
    user_email: str
    full_name: Optional[str] = None
    roles: Optional[List[str]] = None
    permissions: Optional[List[str]] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: JwtPayload

class UserCreate(BaseModel):
    user_email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    user_email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: UUID
    user_email: EmailStr
    full_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True
