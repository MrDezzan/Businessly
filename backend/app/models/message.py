from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class MessageRole(str, enum.Enum):
    USER = "user"       # Message from Telegram user
    ASSISTANT = "assistant"  # AI response
    OWNER = "owner"     # Response from business owner


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, owner
    content = Column(Text, nullable=False)
    telegram_message_id = Column(Integer, nullable=True)  # Original Telegram message ID
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message {self.id} - {self.role}>"
