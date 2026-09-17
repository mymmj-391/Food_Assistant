from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    nickname: str = Field(..., min_length=1, max_length=50, description="昵称")


class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class PublicUser(BaseModel):
    username: str
    nickname: str
    created_at: str
    last_login_at: str


class AuthResponse(BaseModel):
    token: str
    user: PublicUser
