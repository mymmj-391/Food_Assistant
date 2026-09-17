# 健康饮食助手 (Food_Assistant)

基于 FastAPI + Vue 3 + uni-app 的智能饮食助手，集成 AI 对话、菜品知识库、向量检索和用户管理功能。

## ✨ 核心功能

- 🤖 **AI 智能助手** — 基于 RAG 的饮食问答，支持流式输出和工具调用
- 🍳 **菜品知识库** — 10 大分类、150+ 道菜品，包含详细做法和步骤图
- 🧑‍🍳 **厨房技巧** — 烹饪技巧教程，支持步骤教学型展示
- 🔍 **向量检索** — Milvus 向量数据库，语义级知识搜索
- 👤 **用户系统** — 注册登录、收藏管理、饮食记录
- 💬 **聊天历史** — 多轮对话记忆，会话持久化

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | FastAPI + SQLAlchemy (异步) + Pydantic |
| 前端 | Vue 3 + uni-app + Pinia |
| 数据库 | MySQL + Milvus 向量数据库 |
| AI | DeepSeek LLM + BAAI/bge-m3 嵌入模型 |
| 部署 | Docker Compose (Milvus + MinIO + etcd) |

## 📁 项目结构

```
Food_Assistant/
├── app/                        # 后端核心
│   ├── ai/                     # AI 模块 (LLM、嵌入、RAG、知识库)
│   ├── api/                    # API 路由层
│   ├── core/                   # 配置、数据库、向量库
│   ├── schemas/                # 数据模型
│   ├── services/               # 业务逻辑
│   └── models/                 # ORM 模型
├── frontend/                   # Vue3 前端
│   ├── pages/                  # 页面组件
│   ├── components/             # 公共组件
│   ├── api/                    # 请求封装
│   ├── stores/                 # 状态管理
│   └── utils/                  # 工具函数
├── knowledge/                  # 知识库
│   ├── dishes/                 # 菜品 (10 分类, 150+ 道菜)
│   └── tips/                   # 厨房技巧
├── main.py                     # 入口文件
├── import_knowledge.py         # 知识库导入脚本
├── docker-compose.yml          # Milvus 容器编排
└── requirements.txt            # Python 依赖
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 复制环境变量模板
cp .env.example .env
# 编辑 .env 填写必需配置
```

必需的环境变量：
```
DATABASE_URL=mysql+aiomysql://root:密码@localhost:3306/Food_Assistant_Test
DEEPSEEK_API_KEY=sk-xxx
SILICONFLOW_API_KEY=sk-xxx
```

### 2. 启动向量数据库

```bash
docker-compose up -d
```

### 3. 导入知识库

```bash
# 增量导入（默认，MD5 去重）
python import_knowledge.py

# 全量重建
python import_knowledge.py --full-reload
```

### 4. 启动后端

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

后端地址：`http://127.0.0.1:8000`

### 5. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端地址：`http://127.0.0.1:5173`

## 📖 API 文档

启动后端后访问：`http://127.0.0.1:8000/docs`

| 模块 | 主要接口 |
|------|---------|
| 认证 | `POST /api/auth/register` `/login` `/logout` |
| 聊天 | `POST /api/chat/ask` `/stream` `GET /history/{id}` |
| 菜品 | `GET /api/dishes/categories` `/detail/{cat}/{name}` |
| 收藏 | `POST /api/favorites/add` `/remove` `/list` |
| 记录 | `POST /api/favorites/diet/add` `/list` |
| 技巧 | `GET /api/kitchen/tips` `/tips/{name}` |
| 向量 | `POST /api/vector/import` `/search` `/stats` |

## 🔑 外部 API

| 服务 | 用途 | 注册 |
|------|------|------|
| DeepSeek | LLM 对话 | https://platform.deepseek.com/ |
| 硅基流动 | 文本嵌入 | https://siliconflow.cn/ |
| 和风天气 | 天气查询 | https://dev.qweather.com/ |
| 高德地图 | IP 定位 | https://lbs.amap.com/ |

## 📄 知识库导入

```bash
# 增量导入（自动跳过已存在内容）
python import_knowledge.py

# 全量重建（删除旧数据重新导入）
python import_knowledge.py --full-reload
```

导入结果示例：
```
导入完成!
  - 文档块总数: 1200
  - 成功插入: 50
  - 跳过重复: 1150
```

## 📝 License

MIT
