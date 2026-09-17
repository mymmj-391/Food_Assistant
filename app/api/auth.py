from fastapi import APIRouter, HTTPException, Header
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse
from app.services.auth_service import create_user, authenticate_user, logout_user

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    result = await create_user(request.username, request.password, request.nickname)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    # 注册成功后自动登录，返回 token 和 user
    login_result = await authenticate_user(request.username, request.password)
    if not login_result["success"]:
        raise HTTPException(status_code=500, detail="注册成功但自动登录失败，请手动登录")
    return AuthResponse(
        token=login_result["token"],
        user=login_result["user"],
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    result = await authenticate_user(request.username, request.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    return AuthResponse(
        token=result["token"],
        user=result["user"],
    )


@router.post("/logout", response_model=dict)
async def logout(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供认证信息")

    token = authorization.replace("Bearer ", "")
    success = await logout_user(token)
    if not success:
        raise HTTPException(status_code=400, detail="登出失败")
    return {"message": "登出成功"}
