import httpx
from typing import Optional, Dict, Any
from app.config import get_settings

settings = get_settings()


class TelegramService:
    """Service for interacting with Telegram Bot API."""
    
    BASE_URL = "https://api.telegram.org/bot"
    
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a Telegram bot token and get bot info.
        
        Returns bot info if valid, None if invalid.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}{token}/getMe",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        return data.get("result")
                return None
        except Exception:
            return None
    
    async def set_webhook(self, token: str, bot_id: int) -> bool:
        """Set webhook URL for a bot."""
        if not settings.webhook_base_url:
            return False
        
        webhook_url = f"{settings.webhook_base_url}/api/telegram/webhook/{token}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}{token}/setWebhook",
                    json={
                        "url": webhook_url,
                        "allowed_updates": ["message"]
                    },
                    timeout=10.0
                )
                
                data = response.json()
                return data.get("ok", False)
        except Exception:
            return False
    
    async def delete_webhook(self, token: str) -> bool:
        """Remove webhook for a bot."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}{token}/deleteWebhook",
                    timeout=10.0
                )
                
                data = response.json()
                return data.get("ok", False)
        except Exception:
            return False
    
    async def send_message(
        self,
        token: str,
        chat_id: int,
        text: str,
        reply_to_message_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Send a message to a Telegram chat."""
        try:
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            
            if reply_to_message_id:
                payload["reply_to_message_id"] = reply_to_message_id
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}{token}/sendMessage",
                    json=payload,
                    timeout=10.0
                )
                
                data = response.json()
                if data.get("ok"):
                    return data.get("result")
                return None
        except Exception:
            return None
    
    async def send_typing_action(self, token: str, chat_id: int) -> bool:
        """Send typing indicator to a chat."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}{token}/sendChatAction",
                    json={
                        "chat_id": chat_id,
                        "action": "typing"
                    },
                    timeout=5.0
                )
                return response.status_code == 200
        except Exception:
            return False


# Singleton instance
telegram_service = TelegramService()
