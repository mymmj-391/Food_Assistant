from fastapi import APIRouter, HTTPException, Depends
from app.schemas.favorites import FavoriteRequest, DietRecordRequest
from app.services.favorite_service import (
    add_favorite,
    remove_favorite,
    check_favorite,
    get_favorites,
    add_diet_record,
    get_diet_records,
    delete_diet_record,
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/favorites", tags=["收藏与饮食记录"])


@router.post("/add", response_model=dict)
async def favorite_add(
    request: FavoriteRequest,
    user=Depends(get_current_user),
):
    result = await add_favorite(
        user_id=user.username,
        dish_name=request.dish_name,
        category_id=request.category_id,
        category_name=request.category_name,
        image=request.image,
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return {"message": result["message"]}


@router.post("/remove", response_model=dict)
async def favorite_remove(
    request: FavoriteRequest,
    user=Depends(get_current_user),
):
    result = await remove_favorite(
        user_id=user.username,
        dish_name=request.dish_name,
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return {"message": result["message"]}


@router.get("/check", response_model=dict)
async def favorite_check(
    dish_name: str,
    user=Depends(get_current_user),
):
    is_favorite = await check_favorite(user.username, dish_name)
    return {"is_favorite": is_favorite}


@router.get("/list", response_model=list)
async def favorite_list(user=Depends(get_current_user)):
    return await get_favorites(user.username)


@router.post("/diet/add", response_model=dict)
async def diet_add(
    request: DietRecordRequest,
    user=Depends(get_current_user),
):
    result = await add_diet_record(
        user_id=user.username,
        dish_name=request.dish_name,
        category_id=request.category_id,
        category_name=request.category_name,
        image=request.image,
    )
    return {"message": result["message"]}


@router.get("/diet/list", response_model=list)
async def diet_list(user=Depends(get_current_user)):
    return await get_diet_records(user.username)


@router.delete("/diet/delete", response_model=dict)
async def diet_delete(
    id: int,
    user=Depends(get_current_user),
):
    result = await delete_diet_record(user_id=user.username, record_id=id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return {"message": result["message"]}
