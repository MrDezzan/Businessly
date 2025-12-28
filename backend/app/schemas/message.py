from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    id: int
    role: str  # user, assistant, owner
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessagesListResponse(BaseModel):
    conversation_id: int
    is_ai_controlled: bool
    messages: list[MessageResponse]
