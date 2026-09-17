from fastapi import APIRouter, HTTPException
from app.schemas.dish import DishListResponse, DishDetailResponse
from app.services.dish_service import get_tips_list, get_tip_detail

router = APIRouter(prefix="/kitchen", tags=["厨房技巧"])


@router.get("/tips", response_model=DishListResponse)
async def list_tips():
    tips = get_tips_list()
    return DishListResponse(list=tips)


@router.get("/tips/{tip_name}", response_model=DishDetailResponse)
async def get_tip(tip_name: str):
    result = get_tip_detail(tip_name)
    if not result:
        raise HTTPException(status_code=404, detail="技巧不存在")
    return DishDetailResponse(**result)
