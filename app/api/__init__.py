from fastapi import APIRouter
from app.api import auth, dishes, favorites, chat, kitchen, vector, home

api_router = APIRouter()


@api_router.get("/health")
async def health_check():
    """健康检查接口"""
    from app.core.vector_db import has_collection
    from app.core.settings import DEEPSEEK_API_KEY, SILICONFLOW_API_KEY

    milvus_ok = False
    try:
        has_collection()
        milvus_ok = True
    except Exception:
        milvus_ok = False

    return {
        "status": "ok",
        "message": "服务正常运行",
        "checks": {
            "milvus": "connected" if milvus_ok else "disconnected",
            "deepseek_api": "configured" if DEEPSEEK_API_KEY else "missing",
            "siliconflow_api": "configured" if SILICONFLOW_API_KEY else "missing",
        }
    }


api_router.include_router(auth.router)
api_router.include_router(dishes.router)
api_router.include_router(favorites.router)
api_router.include_router(chat.router)
api_router.include_router(kitchen.router)
api_router.include_router(vector.router)
api_router.include_router(home.router)
