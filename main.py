import os
from pathlib import Path
from contextlib import asynccontextmanager

# 加载 .env 文件（必须在导入其他模块之前）
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_path)
    print("已加载环境配置: .env")
else:
    print("警告: 未找到 .env，使用系统环境变量")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.database import init_db, close_db
from app.core.vector_db import get_or_create_collection, close_milvus
from app.core.settings import DISHES_ROOT, TIPS_ROOT
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    get_or_create_collection()
    yield
    await close_db()
    close_milvus()


app = FastAPI(title="Food Assistant API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件服务 - 菜品图片
if Path(DISHES_ROOT).exists():
    app.mount("/api/dishes/image", StaticFiles(directory=DISHES_ROOT), name="dish_images")
    print(f"已挂载菜品图片目录: {DISHES_ROOT}")

# 挂载静态文件服务 - 技巧图片
if Path(TIPS_ROOT).exists():
    app.mount("/api/kitchen/image", StaticFiles(directory=TIPS_ROOT), name="tip_images")
    print(f"已挂载技巧图片目录: {TIPS_ROOT}")

app.include_router(api_router, prefix="/api")

# 挂载前端静态文件（用于 3D 模型等）
_frontend_static = Path(__file__).parent / "frontend" / "static"
if _frontend_static.exists():
    app.mount("/static", StaticFiles(directory=str(_frontend_static)), name="frontend_static")
    print(f"已挂载前端静态目录: {_frontend_static}")


@app.get("/")
async def root():
    return {
        "message": "Food Assistant API",
        "environment": os.getenv("ENV", "production"),
        "debug": os.getenv("DEBUG", "false"),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
