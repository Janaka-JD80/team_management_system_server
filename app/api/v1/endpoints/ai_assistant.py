from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.ai_assistant import ChatRequest, ChatResponse
from app.schemas.base import StandardResponse
from app.schemas.auth import JwtPayload
from app.core.deps import get_current_user,RequireRole
from app.services.ai_assistant_service import ai_assistant_service

router = APIRouter()

@router.post("/chat", response_model=StandardResponse[ChatResponse])
async def ai_chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user: JwtPayload = Depends(RequireRole("manager"))
):
    reply_text = await ai_assistant_service.generate_chat_response(
        db=db, 
        message=request.message, 
    )
    
    return StandardResponse(data=ChatResponse(reply=reply_text))
