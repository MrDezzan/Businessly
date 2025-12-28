from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.database import Base


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("telegram_bots.id"), nullable=False)
    telegram_chat_id = Column(BigInteger, nullable=False)  # Telegram chat ID
    telegram_user_id = Column(BigInteger, nullable=True)  # Telegram user ID
    telegram_username = Column(String(100), nullable=True)  # @username
    telegram_first_name = Column(String(100), nullable=True)
    telegram_last_name = Column(String(100), nullable=True)
    is_ai_controlled = Column(Boolean, default=True)  # AI or manual mode
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bot = relationship("TelegramBot", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation {self.id} - Chat {self.telegram_chat_id}>"
