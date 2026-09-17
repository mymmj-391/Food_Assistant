from datetime import datetime, timedelta
from sqlalchemy import select, delete
from app.models.favorite import FavoriteModel, DietRecordModel
from app.core.database import async_session

KEEP_DAYS = 30


async def add_favorite(user_id: str, dish_name: str, category_id: str, category_name: str, image: str) -> dict:
    async with async_session() as session:
        result = await session.execute(
            select(FavoriteModel).where(
                FavoriteModel.user_id == user_id,
                FavoriteModel.dish_name == dish_name,
            )
        )
        if result.scalar_one_or_none():
            return {"success": False, "message": "已在收藏中"}

        favorite = FavoriteModel(
            user_id=user_id,
            dish_name=dish_name,
            category_id=category_id,
            category_name=category_name,
            image=image,
        )
        session.add(favorite)
        await session.commit()
        return {"success": True, "message": "收藏成功"}


async def remove_favorite(user_id: str, dish_name: str) -> dict:
    async with async_session() as session:
        result = await session.execute(
            select(FavoriteModel).where(
                FavoriteModel.user_id == user_id,
                FavoriteModel.dish_name == dish_name,
            )
        )
        favorite = result.scalar_one_or_none()
        if not favorite:
            return {"success": False, "message": "未找到收藏"}

        await session.delete(favorite)
        await session.commit()
        return {"success": True, "message": "取消收藏成功"}


async def check_favorite(user_id: str, dish_name: str) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(FavoriteModel).where(
                FavoriteModel.user_id == user_id,
                FavoriteModel.dish_name == dish_name,
            )
        )
        return result.scalar_one_or_none() is not None


async def get_favorites(user_id: str) -> list:
    async with async_session() as session:
        result = await session.execute(
            select(FavoriteModel)
            .where(FavoriteModel.user_id == user_id)
            .order_by(FavoriteModel.created_at.desc())
        )
        favorites = result.scalars().all()
        return [
            {
                "id": f.id,
                "dish_name": f.dish_name,
                "category_id": f.category_id,
                "category_name": f.category_name,
                "image": f.image,
                "created_at": f.created_at.strftime("%Y-%m-%d %H:%M:%S") if f.created_at else "",
            }
            for f in favorites
        ]


async def add_diet_record(user_id: str, dish_name: str, category_id: str, category_name: str, image: str) -> dict:
    async with async_session() as session:
        cutoff_date = datetime.now() - timedelta(days=KEEP_DAYS)
        await session.execute(
            delete(DietRecordModel).where(DietRecordModel.viewed_at < cutoff_date)
        )

        # 检查24小时内是否已有相同菜品的记录
        twenty_four_h_ago = datetime.now() - timedelta(hours=24)
        existing = await session.execute(
            select(DietRecordModel).where(
                DietRecordModel.user_id == user_id,
                DietRecordModel.dish_name == dish_name,
                DietRecordModel.viewed_at >= twenty_four_h_ago,
            )
        )
        if existing.scalar_one_or_none():
            return {"success": False, "message": "24小时内已记录过该菜品"}

        record = DietRecordModel(
            user_id=user_id,
            dish_name=dish_name,
            category_id=category_id,
            category_name=category_name,
            image=image,
        )
        session.add(record)
        await session.commit()
        return {"success": True, "message": "记录成功"}


async def get_diet_records(user_id: str) -> list:
    async with async_session() as session:
        cutoff_date = datetime.now() - timedelta(days=KEEP_DAYS)
        result = await session.execute(
            select(DietRecordModel)
            .where(DietRecordModel.user_id == user_id)
            .where(DietRecordModel.viewed_at >= cutoff_date)
            .order_by(DietRecordModel.viewed_at.desc())
        )
        records = result.scalars().all()
        return [
            {
                "id": r.id,
                "dish_name": r.dish_name,
                "category_id": r.category_id,
                "category_name": r.category_name,
                "image": r.image,
                "viewed_at": r.viewed_at.strftime("%Y-%m-%d %H:%M:%S") if r.viewed_at else "",
            }
            for r in records
        ]


async def delete_diet_record(user_id: str, record_id: int) -> dict:
    async with async_session() as session:
        result = await session.execute(
            select(DietRecordModel).where(
                DietRecordModel.id == record_id,
                DietRecordModel.user_id == user_id,
            )
        )
        record = result.scalar_one_or_none()
        if not record:
            return {"success": False, "message": "记录不存在"}
        await session.delete(record)
        await session.commit()
        return {"success": True, "message": "删除成功"}
