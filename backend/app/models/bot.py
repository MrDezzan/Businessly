from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class TelegramBot(Base):
    __tablename__ = "telegram_bots"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    bot_id = Column(String(50), nullable=True)  # Telegram bot ID
    bot_username = Column(String(100), nullable=True)  # @username
    name = Column(String(100), nullable=False)  # Display name
    business_description = Column(Text, nullable=False)  # Business context for AI
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="bots")
    conversations = relationship("Conversation", back_populates="bot", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TelegramBot {self.name}>"
