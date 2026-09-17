from fastapi import APIRouter

router = APIRouter(prefix="/home", tags=["首页"])


@router.get("/stats", response_model=dict)
async def home_stats():
    from app.ai.knowledge import get_stats
    from app.services.dish_service import get_category_list

    try:
        vector_stats = get_stats()
    except Exception:
        vector_stats = {"exists": False, "row_count": 0, "total_vectors": 0, "error": "milvus_unavailable"}

    categories = get_category_list()

    return {
        "vector_stats": vector_stats,
        "categories": categories,
    }
