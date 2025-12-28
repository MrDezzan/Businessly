from app.routers.auth import router as auth_router
from app.routers.bots import router as bots_router
from app.routers.conversations import router as conversations_router
from app.routers.telegram import router as telegram_router

__all__ = ["auth_router", "bots_router", "conversations_router", "telegram_router"]
