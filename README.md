# 影视漫剧 AI 生产中台 MVP

第一阶段 MVP，覆盖：项目管理、角色库、场景库、镜头表（含增删改）、提示词模板、Mock 生成任务、资产库页面。

## 技术栈
- Frontend: Next.js + TypeScript + TailwindCSS + shadcn/ui 风格组件
- Backend: FastAPI + Python
- DB: PostgreSQL
- Queue: Redis + RQ
- Object Storage: MinIO (local)
- Deploy: Docker Compose

## 目录结构

```text
.
├── frontend/                     # Next.js 前端
│   ├── src/app/
│   │   ├── page.tsx              # 仪表盘
│   │   ├── projects/page.tsx
│   │   ├── characters/page.tsx
│   │   ├── scenes/page.tsx
│   │   ├── shots/page.tsx
│   │   ├── prompts/page.tsx
│   │   ├── tasks/page.tsx
│   │   └── assets/page.tsx
│   └── ...
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI 入口
│   │   ├── api/routes.py         # 路由
│   │   ├── models/               # SQLAlchemy 模型
│   │   ├── schemas/              # Pydantic 模型
│   │   ├── services/mock_provider.py
│   │   └── worker/worker.py      # RQ worker
│   ├── migrations/sql/001_init.sql
│   └── requirements.txt
├── docker-compose.yml
├── .env.example
└── Makefile
```

## 快速启动

1) 复制环境变量：
```bash
cp .env.example .env
```

2) 启动所有服务：
```bash
docker compose up --build
```

3) 执行数据库初始化（首次）：
```bash
docker compose exec backend psql "$DATABASE_URL" -f /app/migrations/sql/001_init.sql
docker compose exec backend psql "$DATABASE_URL" -f /app/migrations/sql/002_shots_expand.sql
```

4) 访问：
- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

## 常用命令

```bash
make up          # 启动
make down        # 停止
make logs        # 查看日志
make migrate     # 执行 SQL 迁移
make test-backend # 在 backend 容器内运行后端测试
```

## Mock 生成任务说明
- 当前不对接真实 AI API。
- `POST /api/tasks/mock-generate` 会创建任务并入队。
- RQ worker 会调用 mock provider 生成伪结果，更新任务状态为 `done`。



## 镜头管理模块（Shots）
- 后端 REST API：`GET /api/shots`、`POST /api/shots`、`PUT /api/shots/{id}`、`DELETE /api/shots/{id}`。
- 字段：集数、场次、镜头号、时长、画幅、景别、机位、动作、台词、视觉要求、负面提示词、状态。
- 前端页面：`/shots`，采用「表格 + 详情抽屉」交互。


## OpenAI image adapter
- 环境变量：`OPENAI_API_KEY`（仅从环境变量读取，不写入代码）。
- 入队接口：`POST /api/tasks/openai-image-generate`（文生图）、`POST /api/tasks/openai-image-edit`（图生图编辑）。
- 任务记录会保存：请求参数、响应载荷、成本估算、错误原因。
