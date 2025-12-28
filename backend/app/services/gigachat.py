import httpx
import uuid
import ssl
from typing import Optional, Tuple
from datetime import datetime, timedelta
from app.config import get_settings

settings = get_settings()


class GigaChatService:
    """Service for interacting with GigaChat API from Sber."""
    
    def __init__(self):
        self.auth_key = settings.gigachat_auth_key
        self.scope = settings.gigachat_scope
        self.oauth_url = settings.gigachat_oauth_url
        self.api_url = settings.gigachat_api_url
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
    
    async def _get_access_token(self) -> str:
        """Get or refresh access token for GigaChat API."""
        # Check if we have a valid token
        if self.access_token and self.token_expires_at:
            if datetime.utcnow() < self.token_expires_at - timedelta(minutes=1):
                return self.access_token
        
        # Request new token
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4()),
            "Authorization": f"Basic {self.auth_key}"
        }
        
        data = {"scope": self.scope}
        
        # GigaChat uses self-signed certificates
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(
                self.oauth_url,
                headers=headers,
                data=data,
                timeout=30.0
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            # Token expires in 30 minutes
            self.token_expires_at = datetime.utcnow() + timedelta(minutes=30)
            
            return self.access_token
    
    async def generate_response(
        self,
        user_message: str,
        business_description: str,
        conversation_history: list[dict] = None
    ) -> Tuple[str, float]:
        """
        Generate AI response for a user message.
        
        Returns:
            Tuple of (response_text, confidence_score)
            confidence_score: 0.0-1.0, higher means AI is more confident
        """
        access_token = await self._get_access_token()
        
        # Build messages for context
        messages = [
            {
                "role": "system",
                "content": f"""Ты — AI-консультант для бизнеса. Отвечай профессионально и дружелюбно.

Описание бизнеса:
{business_description}

Правила:
1. Отвечай только на вопросы, связанные с данным бизнесом
2. Если не знаешь точного ответа — честно скажи об этом
3. Если вопрос требует ручного вмешательства владельца — укажи это
4. Отвечай кратко и по делу
5. Используй вежливый тон

Если ты НЕ УВЕРЕН в ответе или вопрос слишком сложный, начни ответ с [UNSURE]."""
            }
        ]
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-10:]:  # Last 10 messages
                messages.append({
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["content"]
                })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        payload = {
            "model": "GigaChat",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            
            # Calculate confidence based on response
            confidence = 0.8  # Default confidence
            
            # Lower confidence if AI indicates uncertainty
            if ai_response.startswith("[UNSURE]"):
                confidence = 0.3
                ai_response = ai_response.replace("[UNSURE]", "").strip()
            
            # Lower confidence for certain phrases
            uncertainty_phrases = [
                "не уверен", "не знаю", "возможно", "вероятно",
                "лучше спросить", "свяжитесь с", "уточните у"
            ]
            for phrase in uncertainty_phrases:
                if phrase.lower() in ai_response.lower():
                    confidence = min(confidence, 0.5)
                    break
            
            return ai_response, confidence
    
    async def check_health(self) -> bool:
        """Check if GigaChat API is accessible."""
        try:
            await self._get_access_token()
            return True
        except Exception:
            return False


# Singleton instance
gigachat_service = GigaChatService()
