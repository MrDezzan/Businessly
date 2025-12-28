from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ConversationResponse(BaseModel):
    id: int
    telegram_chat_id: int
    telegram_username: Optional[str]
    telegram_first_name: Optional[str]
    telegram_last_name: Optional[str]
    is_ai_controlled: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_message: Optional[str] = None
    unread_count: int = 0
    
    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    id: int
    telegram_username: Optional[str]
    telegram_first_name: Optional[str]
    is_ai_controlled: bool
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    unread_count: int = 0
    
    class Config:
        from_attributes = True


class ControlToggle(BaseModel):
    is_ai_controlled: bool
