from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.bot import TelegramBot
from app.models.conversation import Conversation
from app.schemas.bot import BotCreate, BotUpdate, BotResponse, BotListResponse
from app.security import get_current_user, sanitize_input
from app.services.telegram import telegram_service

router = APIRouter(prefix="/api/bots", tags=["Bots"])


@router.post("/", response_model=BotResponse, status_code=status.HTTP_201_CREATED)
async def create_bot(
    bot_data: BotCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a new Telegram bot."""
    # Sanitize inputs
    token = bot_data.token.strip()
    name = sanitize_input(bot_data.name)
    business_description = sanitize_input(bot_data.business_description)
    
    # Check if token already registered
    result = await db.execute(select(TelegramBot).where(TelegramBot.token == token))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This bot token is already registered"
        )
    
    # Validate token with Telegram API
    bot_info = await telegram_service.validate_token(token)
    if not bot_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid bot token. Please check the token from BotFather."
        )
    
    # Create bot
    bot = TelegramBot(
        user_id=current_user.id,
        token=token,
        bot_id=str(bot_info.get("id")),
        bot_username=bot_info.get("username"),
        name=name,
        business_description=business_description,
        is_active=False
    )
    db.add(bot)
    await db.commit()
    await db.refresh(bot)
    
    return BotResponse(
        id=bot.id,
        name=bot.name,
        bot_username=bot.bot_username,
        business_description=bot.business_description,
        is_active=bot.is_active,
        created_at=bot.created_at,
        conversations_count=0
    )


@router.get("/", response_model=List[BotListResponse])
async def list_bots(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all bots for current user."""
    result = await db.execute(
        select(TelegramBot).where(TelegramBot.user_id == current_user.id)
    )
    bots = result.scalars().all()
    
    response = []
    for bot in bots:
        # Count conversations
        conv_result = await db.execute(
            select(func.count(Conversation.id)).where(Conversation.bot_id == bot.id)
        )
        conv_count = conv_result.scalar() or 0
        
        response.append(BotListResponse(
            id=bot.id,
            name=bot.name,
            bot_username=bot.bot_username,
            is_active=bot.is_active,
            conversations_count=conv_count
        ))
    
    return response


@router.get("/{bot_id}", response_model=BotResponse)
async def get_bot(
    bot_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get bot details."""
    result = await db.execute(
        select(TelegramBot).where(
            TelegramBot.id == bot_id,
            TelegramBot.user_id == current_user.id
        )
    )
    bot = result.scalar_one_or_none()
    
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")
    
    # Count conversations
    conv_result = await db.execute(
        select(func.count(Conversation.id)).where(Conversation.bot_id == bot.id)
    )
    conv_count = conv_result.scalar() or 0
    
    return BotResponse(
        id=bot.id,
        name=bot.name,
        bot_username=bot.bot_username,
        business_description=bot.business_description,
        is_active=bot.is_active,
        created_at=bot.created_at,
        conversations_count=conv_count
    )


@router.put("/{bot_id}/toggle")
async def toggle_bot(
    bot_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Toggle bot active status (start/stop)."""
    result = await db.execute(
        select(TelegramBot).where(
            TelegramBot.id == bot_id,
            TelegramBot.user_id == current_user.id
        )
    )
    bot = result.scalar_one_or_none()
    
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")
    
    if bot.is_active:
        # Deactivate - remove webhook
        await telegram_service.delete_webhook(bot.token)
        bot.is_active = False
    else:
        # Activate - set webhook
        success = await telegram_service.set_webhook(bot.token, bot.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to set webhook. Check WEBHOOK_BASE_URL configuration."
            )
        bot.is_active = True
    
    await db.commit()
    
    return {"is_active": bot.is_active}


@router.delete("/{bot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bot(
    bot_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a bot."""
    result = await db.execute(
        select(TelegramBot).where(
            TelegramBot.id == bot_id,
            TelegramBot.user_id == current_user.id
        )
    )
    bot = result.scalar_one_or_none()
    
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")
    
    # Remove webhook if active
    if bot.is_active:
        await telegram_service.delete_webhook(bot.token)
    
    await db.delete(bot)
    await db.commit()
