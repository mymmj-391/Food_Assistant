# Food Assistant

一个基于 `FastAPI + Vue3` 的前后端分离示例项目，当前已完成：

- 登录页

- 注册页

- 主界面

- 基础登录鉴权接口

## 目录结构

```text
Food_Assistant/
├─ main.py                 # FastAPI 后端入口
├─ test_main.http          # HTTP 接口测试文件
├─ frontend/               # Vue3 前端工程
│  ├─ src/
│  │  ├─ views/            # 登录、注册、主页
│  │  ├─ router/           # 路由与登录守卫
│  │  ├─ utils/            # Axios 请求封装
│  │  └─ assets/           # 全局样式
```

## 后端启动

先安装依赖：

```bash
pip install fastapi uvicorn
```

启动服务：

```bash
uvicorn main:app --reload
```

默认地址：

- 后端接口：`http://127.0.0.1:8000`

## 前端启动

进入前端目录安装依赖：

```bash
cd frontend
npm install
```

启动开发环境：

```bash
npm run dev
```

默认地址：

- 前端页面：`http://127.0.0.1:5173`

## 当前接口

- `POST /api/auth/register` 注册

- `POST /api/auth/login` 登录

- `GET /api/auth/me` 获取当前用户

- `GET /api/home/summary` 获取主页摘要



