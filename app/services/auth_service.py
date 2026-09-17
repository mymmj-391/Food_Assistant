import secrets
from datetime import datetime
from sqlalchemy import select
import bcrypt
from app.models.user import UserModel
from app.models.token import TokenModel
from app.core.database import async_session


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except (ValueError, AttributeError):
        return False


async def create_user(username: str, password: str, nickname: str) -> dict:
    async with async_session() as session:
        result = await session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        if result.scalar_one_or_none():
            return {"success": False, "message": "用户名已存在"}

        user = UserModel(
            username=username,
            password=hash_password(password),
            nickname=nickname,
        )
        session.add(user)
        await session.commit()
        return {"success": True, "message": "注册成功"}


async def authenticate_user(username: str, password: str) -> dict:
    async with async_session() as session:
        result = await session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.password):
            return {"success": False, "message": "用户名或密码错误"}

        user.last_login_at = datetime.now()
        await session.commit()

        token = secrets.token_hex(32)
        token_record = TokenModel(token=token, username=username)
        session.add(token_record)
        await session.commit()

        return {
            "success": True,
            "token": token,
            "user": {
                "username": user.username,
                "nickname": user.nickname,
                "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "",
                "last_login_at": user.last_login_at.strftime("%Y-%m-%d %H:%M:%S") if user.last_login_at else "",
            }
        }


async def get_user_by_token(token: str) -> UserModel | None:
    async with async_session() as session:
        result = await session.execute(
            select(TokenModel).where(TokenModel.token == token)
        )
        token_record = result.scalar_one_or_none()

        if not token_record:
            return None

        result = await session.execute(
            select(UserModel).where(UserModel.username == token_record.username)
        )
        return result.scalar_one_or_none()


async def logout_user(token: str) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(TokenModel).where(TokenModel.token == token)
        )
        token_record = result.scalar_one_or_none()

        if not token_record:
            return False

        await session.delete(token_record)
        await session.commit()
        return True
