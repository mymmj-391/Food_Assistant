from fastapi import APIRouter, Depends
from app.ai.knowledge import import_knowledge, search_knowledge, get_stats
from app.dependencies import get_current_user

router = APIRouter(prefix="/vector", tags=["向量检索"])


@router.post("/import", response_model=dict)
async def vector_import(full_reload: bool = False, user=Depends(get_current_user)):
    return import_knowledge(full_reload=full_reload)


@router.get("/search", response_model=list)
async def vector_search(query: str, top_k: int = 5):
    return search_knowledge(query, top_k=top_k)


@router.get("/stats", response_model=dict)
async def vector_stats():
    return get_stats()
