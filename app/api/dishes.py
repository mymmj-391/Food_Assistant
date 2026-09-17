from fastapi import APIRouter, HTTPException
from app.schemas.dish import DishListResponse, DishDetailResponse, DishImageResponse
from app.services.dish_service import (
    get_category_list,
    get_dish_list,
    get_dish_detail,
    get_dish_images,
)

router = APIRouter(prefix="/dishes", tags=["菜品"])


@router.get("/categories", response_model=list)
async def list_categories():
    return get_category_list()


@router.get("/category/{category_id}", response_model=DishListResponse)
async def list_dishes(category_id: str):
    dishes = get_dish_list(category_id)
    return DishListResponse(list=dishes)


@router.get("/detail/{category_id}/{dish_name}", response_model=DishDetailResponse)
async def get_dish(category_id: str, dish_name: str):
    result = get_dish_detail(category_id, dish_name)
    if not result:
        raise HTTPException(status_code=404, detail="菜品不存在")
    return DishDetailResponse(**result)


@router.get("/images/{category_id}/{dish_name}", response_model=DishImageResponse)
async def get_images(category_id: str, dish_name: str):
    images = get_dish_images(category_id, dish_name)
    return DishImageResponse(images=images)
