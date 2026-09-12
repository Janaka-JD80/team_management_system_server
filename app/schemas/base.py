from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

class StandardResponse(BaseModel, Generic[T]):
    status: bool = True
    message: str = "Success"
    data: Optional[T] = None
