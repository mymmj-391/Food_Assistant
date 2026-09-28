from fastapi import APIRouter
from app.api import auth, dishes, favorites, chat, kitchen, vector, home, system

api_router = APIRouter()

api_router.include_router(system.router)
api_router.include_router(auth.router)
api_router.include_router(dishes.router)
api_router.include_router(favorites.router)
api_router.include_router(chat.router)
api_router.include_router(kitchen.router)
api_router.include_router(vector.router)
api_router.include_router(home.router)
