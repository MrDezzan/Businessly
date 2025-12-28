from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BotCreate(BaseModel):
    token: str = Field(..., min_length=40, description="Telegram bot token from BotFather")
    name: str = Field(..., min_length=1, max_length=100)
    business_description: str = Field(..., min_length=10, description="Description of your business for AI context")


class BotUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    business_description: Optional[str] = Field(None, min_length=10)


class BotResponse(BaseModel):
    id: int
    name: str
    bot_username: Optional[str]
    business_description: str
    is_active: bool
    created_at: datetime
    conversations_count: int = 0
    
    class Config:
        from_attributes = True


class BotListResponse(BaseModel):
    id: int
    name: str
    bot_username: Optional[str]
    is_active: bool
    conversations_count: int = 0
    
    class Config:
        from_attributes = True
