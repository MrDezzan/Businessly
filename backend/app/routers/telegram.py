from fastapi import APIRouter, Request, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any, Dict

from app.database import async_session_maker
from app.models.bot import TelegramBot
from app.models.conversation import Conversation
from app.models.message import Message
from app.services.telegram import telegram_service
from app.services.gigachat import gigachat_service
from app.security import sanitize_html

router = APIRouter(prefix="/api/telegram", tags=["Telegram Webhook"])

# Confidence threshold - below this, AI won't respond automatically
CONFIDENCE_THRESHOLD = 0.6


async def process_message(bot_token: str, chat_id: int, user_message: str, message_id: int, user_info: dict):
    """Process incoming message in background."""
    async with async_session_maker() as db:
        try:
            # Find bot
            result = await db.execute(
                select(TelegramBot).where(
                    TelegramBot.token == bot_token,
                    TelegramBot.is_active == True
                )
            )
            bot = result.scalar_one_or_none()
            
            if not bot:
                return
            
            # Find or create conversation
            conv_result = await db.execute(
                select(Conversation).where(
                    Conversation.bot_id == bot.id,
                    Conversation.telegram_chat_id == chat_id
                )
            )
            conversation = conv_result.scalar_one_or_none()
            
            if not conversation:
                conversation = Conversation(
                    bot_id=bot.id,
                    telegram_chat_id=chat_id,
                    telegram_user_id=user_info.get("id"),
                    telegram_username=user_info.get("username"),
                    telegram_first_name=user_info.get("first_name"),
                    telegram_last_name=user_info.get("last_name"),
                    is_ai_controlled=True
                )
                db.add(conversation)
                await db.commit()
                await db.refresh(conversation)
            
            # Save user message
            sanitized_message = sanitize_html(user_message)
            user_msg = Message(
                conversation_id=conversation.id,
                role="user",
                content=sanitized_message,
                telegram_message_id=message_id
            )
            db.add(user_msg)
            await db.commit()
            
            # Check if AI should respond
            if not conversation.is_ai_controlled:
                return  # Manual mode - don't respond
            
            # Send typing indicator
            await telegram_service.send_typing_action(bot.token, chat_id)
            
            # Get conversation history
            history_result = await db.execute(
                select(Message)
                .where(Message.conversation_id == conversation.id)
                .order_by(Message.created_at)
                .limit(20)
            )
            history = history_result.scalars().all()
            history_list = [{"role": m.role, "content": m.content} for m in history]
            
            # Generate AI response
            try:
                ai_response, confidence = await gigachat_service.generate_response(
                    user_message=sanitized_message,
                    business_description=bot.business_description,
                    conversation_history=history_list
                )
            except Exception as e:
                # GigaChat error - switch to manual mode
                conversation.is_ai_controlled = False
                await db.commit()
                return
            
            # Check confidence threshold
            if confidence < CONFIDENCE_THRESHOLD:
                # Low confidence - switch to manual mode, notify owner could be added here
                conversation.is_ai_controlled = False
                await db.commit()
                
                # Optionally send a message that owner will respond
                await telegram_service.send_message(
                    bot.token,
                    chat_id,
                    "Ваш вопрос передан менеджеру. Он ответит вам в ближайшее время."
                )
                return
            
            # Send AI response
            tg_result = await telegram_service.send_message(
                bot.token,
                chat_id,
                ai_response
            )
            
            if tg_result:
                # Save AI message
                ai_msg = Message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=ai_response,
                    telegram_message_id=tg_result.get("message_id")
                )
                db.add(ai_msg)
                await db.commit()
                
        except Exception as e:
            print(f"Error processing message: {e}")
            await db.rollback()


@router.post("/webhook/{bot_token}")
async def telegram_webhook(
    bot_token: str,
    request: Request,
    background_tasks: BackgroundTasks
):
    """Handle incoming Telegram webhook."""
    try:
        update: Dict[str, Any] = await request.json()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON")
    
    # Only process messages
    if "message" not in update:
        return {"ok": True}
    
    message = update["message"]
    
    # Only process text messages
    if "text" not in message:
        return {"ok": True}
    
    chat_id = message["chat"]["id"]
    text = message["text"]
    message_id = message["message_id"]
    user_info = message.get("from", {})
    
    # Process in background to respond quickly
    background_tasks.add_task(
        process_message,
        bot_token,
        chat_id,
        text,
        message_id,
        user_info
    )
    
    return {"ok": True}
