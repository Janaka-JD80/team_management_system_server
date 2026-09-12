from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import UserCreate, UserLogin, JwtPayload, TokenResponse
from app.schemas.base import StandardResponse
from app.services.auth_service import auth_service

router = APIRouter()

@router.post("/signup", response_model=StandardResponse[TokenResponse], status_code=status.HTTP_200_OK)
async def signup(
    new_user: UserCreate, 
    response: Response, 
    db: AsyncSession = Depends(get_db)
):
    access_token, payload = await auth_service.signup_user(db, new_user)
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=True
    )
    return StandardResponse(data=TokenResponse(access_token=access_token, user=payload))

@router.post("/login", response_model=StandardResponse[TokenResponse])
async def login(
    credentials: UserLogin, 
    response: Response, 
    db: AsyncSession = Depends(get_db)
):
    access_token, payload = await auth_service.authenticate_user(db, credentials)
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=True
    )
    return StandardResponse(data=TokenResponse(access_token=access_token, user=payload))

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=True
    )
    return StandardResponse(message="Successfully logged out")
