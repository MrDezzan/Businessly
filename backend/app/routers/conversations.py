from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.bot import TelegramBot
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.conversation import ConversationResponse, ConversationListResponse, ControlToggle
from app.schemas.message import MessageCreate, MessageResponse, MessagesListResponse
from app.security import get_current_user, sanitize_input
from app.services.telegram import telegram_service

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


@router.get("/", response_model=List[ConversationListResponse])
async def list_conversations(
    bot_id: int = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all conversations for user's bots."""
    # Get user's bots
    if bot_id:
        bot_query = select(TelegramBot).where(
            TelegramBot.id == bot_id,
            TelegramBot.user_id == current_user.id
        )
    else:
        bot_query = select(TelegramBot).where(TelegramBot.user_id == current_user.id)
    
    bots_result = await db.execute(bot_query)
    bots = bots_result.scalars().all()
    bot_ids = [b.id for b in bots]
    
    if not bot_ids:
        return []
    
    # Get conversations
    result = await db.execute(
        select(Conversation)
        .where(Conversation.bot_id.in_(bot_ids))
        .order_by(desc(Conversation.updated_at))
    )
    conversations = result.scalars().all()
    
    response = []
    for conv in conversations:
        # Get last message
        msg_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(desc(Message.created_at))
            .limit(1)
        )
        last_msg = msg_result.scalar_one_or_none()
        
        response.append(ConversationListResponse(
            id=conv.id,
            telegram_username=conv.telegram_username,
            telegram_first_name=conv.telegram_first_name,
            is_ai_controlled=conv.is_ai_controlled,
            last_message=last_msg.content[:50] if last_msg else None,
            last_message_at=last_msg.created_at if last_msg else None,
            unread_count=0
        ))
    
    return response


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get conversation details."""
    # Get conversation with bot check
    result = await db.execute(
        select(Conversation, TelegramBot)
        .join(TelegramBot)
        .where(
            Conversation.id == conversation_id,
            TelegramBot.user_id == current_user.id
        )
    )
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    
    conv, bot = row
    
    return ConversationResponse(
        id=conv.id,
        telegram_chat_id=conv.telegram_chat_id,
        telegram_username=conv.telegram_username,
        telegram_first_name=conv.telegram_first_name,
        telegram_last_name=conv.telegram_last_name,
        is_ai_controlled=conv.is_ai_controlled,
        is_active=conv.is_active,
        created_at=conv.created_at,
        updated_at=conv.updated_at
    )


@router.get("/{conversation_id}/messages", response_model=MessagesListResponse)
async def get_messages(
    conversation_id: int,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a conversation."""
    # Verify ownership
    result = await db.execute(
        select(Conversation, TelegramBot)
        .join(TelegramBot)
        .where(
            Conversation.id == conversation_id,
            TelegramBot.user_id == current_user.id
        )
    )
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    
    conv, bot = row
    
    # Get messages
    msg_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .limit(limit)
    )
    messages = msg_result.scalars().all()
    
    return MessagesListResponse(
        conversation_id=conv.id,
        is_ai_controlled=conv.is_ai_controlled,
        messages=[MessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            created_at=m.created_at
        ) for m in messages]
    )


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message as the business owner."""
    # Verify ownership and get bot token
    result = await db.execute(
        select(Conversation, TelegramBot)
        .join(TelegramBot)
        .where(
            Conversation.id == conversation_id,
            TelegramBot.user_id == current_user.id
        )
    )
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    
    conv, bot = row
    
    # Sanitize content
    content = sanitize_input(message_data.content)
    
    # Send message via Telegram
    tg_result = await telegram_service.send_message(
        bot.token,
        conv.telegram_chat_id,
        content
    )
    
    if not tg_result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message to Telegram"
        )
    
    # Save message
    message = Message(
        conversation_id=conv.id,
        role="owner",
        content=content,
        telegram_message_id=tg_result.get("message_id")
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    
    return MessageResponse(
        id=message.id,
        role=message.role,
        content=message.content,
        created_at=message.created_at
    )


@router.put("/{conversation_id}/control")
async def toggle_control(
    conversation_id: int,
    control_data: ControlToggle,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Toggle AI/manual control for a conversation."""
    # Verify ownership
    result = await db.execute(
        select(Conversation, TelegramBot)
        .join(TelegramBot)
        .where(
            Conversation.id == conversation_id,
            TelegramBot.user_id == current_user.id
        )
    )
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    
    conv, bot = row
    conv.is_ai_controlled = control_data.is_ai_controlled
    await db.commit()
    
    return {"is_ai_controlled": conv.is_ai_controlled}
