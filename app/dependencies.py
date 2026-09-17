from fastapi import Header, HTTPException
from app.services.auth_service import get_user_by_token


async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供认证信息")

    token = authorization.replace("Bearer ", "")
    user = await get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="认证失败或已过期")

    return user


async def get_current_user_optional(authorization: str = Header(None)):
    """可选认证，未登录（无 Authorization 头）时返回 None"""
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.replace("Bearer ", "")
    user = await get_user_by_token(token)
    return user
