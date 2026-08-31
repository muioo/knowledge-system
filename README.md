# knowledge-system 知识管理系统

基于 **FastAPI + React** 的个人知识管理系统。支持用户认证、多级标签管理、文章上传、URL 导入、HTML 内容存储、阅读记录与阅读统计。

## 功能特性

- 用户认证与鉴权（JWT，支持 Token 自动刷新）
- 多级标签（`parent_id` 建立任意深度层级，按父标签筛选自动包含全部后代）
- 文章 CRUD、多格式文档上传自动转 Markdown、URL 导入
- URL 导入可选用**智谱大模型**（`glm-4-flash`）提取标题、正文、摘要与关键词
- 公众号 / 知乎等站点级抓取适配
- 阅读历史、阅读统计、阅读趋势与时间分布
- Swagger API 文档

## 技术栈

| 层 | 技术 |
| --- | --- |
| 后端 | FastAPI · TortoiseORM · Pydantic v2 · Aerich |
| 数据库 | MySQL 8.0+ |
| 前端 | React 19 · Vite · TypeScript · TailwindCSS · Recharts |
| 部署 | Docker Compose（MySQL + 后端 + 前端一键启动） |

## 项目结构

```
.
├── backend/                 # FastAPI 后端
│   ├── api/v1/endpoints/    # API 路由层
│   ├── services/            # 接口业务层（*_service.py）
│   ├── ai/                  # AI 集成层（AI 供应商提取）
│   ├── storage/             # 文章存储层（HTML 持久化）
│   ├── models/              # TortoiseORM 数据模型
│   ├── schemas/             # Pydantic 请求/响应模型
│   ├── migrations/          # Aerich 迁移文件
│   ├── utils/               # 纯工具类（HTML 抓取、文档转换等）
│   └── main.py              # 应用入口（端口 8022）
├── frontend/                # React + Vite 前端（端口 5173）
├── docker-compose.yml       # 一键部署编排
└── docs/                    # 项目文档
```

---

## 一、Docker 一键部署（推荐）

需要本机已安装 **Docker** 与 **Docker Compose** 插件（`docker compose version` 可用）。

### 1. 准备环境变量（可选）

内置了可直接运行的开发默认值，默认情况下**无需任何配置**即可启动。如需自定义数据库密码等，在项目根目录新建 `.env`：

```env
# 以下均为可选，不填则使用默认值
SECRET_KEY=change-me-in-production
MYSQL_ROOT_PASSWORD=root
DB_NAME=knowledge_system
DB_USER=knowledge_user
DB_PASSWORD=Knowledge@123
# 前端对外端口（默认 5173）
FRONTEND_PORT=5173
# AI 供应商密钥（可选，仅后端持有）：智谱 / 千问（百炼）/ 自定义 OpenAI 兼容
ZHIPU_API_KEY=
DASHSCOPE_API_KEY=
DASHSCOPE_WORKSPACE_ID=
CUSTOM_API_KEY=
CUSTOM_BASE_URL=
```

> 变量模板见 [backend/.env.example](backend/.env.example)。密钥类信息请勿提交到 Git。

### 2. 一键构建并启动

```bash
docker compose up -d --build
```

首次构建需拉取基础镜像并编译前端，耗时较长，请耐心等待。可用 `docker compose ps` 与健康检查 `http://localhost:8022/health` 确认后端就绪。

> **无需导出/导入数据库**：全新机器上首次启动会自动建表（entrypoint 会执行迁移或在空库直接建表），无需任何数据迁移；首次使用直接“注册”账号即可。

### 3. 验证与访问

- 查看各容器运行状态：

  ```bash
  docker compose ps
  ```

- 浏览器访问：**http://localhost:5173**（前端）
- 后端 API 文档：**http://localhost:8022/docs**（Swagger）
- 健康检查：**http://localhost:8022/health** → 返回 `{"status":"ok"}`

登录账号可二选一：

- 打开前端页面后，通过“注册”接口创建新账号；
- 或进入后端容器创建管理员：`docker exec -it knowledge-backend python backend/create_admin.py`（管理员 `wbl / wbl@123456`）。

### 4. 停止 / 清理

```bash
docker compose down                # 停止并移除容器（保留数据）
docker compose down -v             # 连数据库数据卷一并删除，回到全新态（下次启动需重新注册账号）
```

> 后端会自动执行 Aerich 数据库迁移并等待 MySQL 就绪，无需手动建库。

---

## 二、本地开发启动

### 1. 后端

要求：Python 3.11、本机 MySQL 8.0+、conda（可选）。

```bash
# 创建并激活虚拟环境
conda create -n knowledge-system python=3.11
conda activate knowledge-system
pip install -r backend/requirements.txt
```

配置环境变量，将 `backend/.env.example` 复制为后端配置文件：

```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env，按需修改 SECRET_KEY、DB_* 项
```

在 MySQL 中创建数据库（库名需与 `.env` 的 `DB_NAME` 一致）：

```sql
CREATE DATABASE IF NOT EXISTS knowledge_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

执行数据库迁移并创建管理员：

```bash
# 首次从空库启动，若已有迁移记录则用 aerich upgrade
aerich upgrade
# 创建管理员 wbl / wbl@123456
python backend/create_admin.py
```

启动后端服务（端口 8022）：

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8022
```

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

打开 **http://localhost:5173** 即可。开发模式下 `/api` 请求会由 Vite 代理到后端 `http://localhost:8022`。

---

## 三、配置项说明

| 变量 | 说明 | 默认 |
| --- | --- | --- |
| `SECRET_KEY` | JWT 签名密钥（生产环境务必修改） | — |
| `DB_HOST / DB_PORT / DB_USER / DB_PASSWORD / DB_NAME` | 数据库连接 | localhost / 3306 / root / — / knowledge_system |
| `CORS_ORIGINS` | 允许的前端站点（JSON 数组） | `["http://localhost:5173"]` |
| `BASE_URL` | 服务器外部访问地址（用于生成图片链接），部署时改为实际地址 | `http://localhost:5173` |
| `MAX_FILE_SIZE` | 上传大小上限（字节） | `10485760`（10MB） |
| `ZHIPU_API_KEY` | 智谱 AI 密钥（可选，仅后端读取） | 空 |
| `DASHSCOPE_API_KEY` / `DASHSCOPE_WORKSPACE_ID` | 千问（百炼）密钥与业务 ID，base_url 自动拼接 | 空 |
| `CUSTOM_API_KEY` / `CUSTOM_BASE_URL` | 自定义 OpenAI 兼容供应商（DeepSeek 官方、自建 vLLM 等） | 空 |
| `*_DEFAULT_MODEL` | 各供应商服务端默认模型，可被用户绑定模型覆盖 | 见 `backend/.env.example` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` / `REFRESH_TOKEN_EXPIRE_DAYS` | Token 有效期 | 30 / 7 |

> 所有 AI 供应商密钥只从后端环境变量读取，前端不会采集或发送任何密钥。**URL 导入时的模型选择为用户级配置**：登录用户在导入页选择供应商并录入模型，保存后长期绑定账号（存于 `user_ai_settings` 表），下次自动回填；未绑定时使用服务端默认模型。

---

## 四、测试

```bash
# 后端测试
cd backend && pytest

# 前端测试与构建检查
cd frontend && npm run test && npm run build
```

## 五、文档

- [API 文档](docs/API_DOCUMENTATION.md)
- [数据库迁移指南](docs/DATABASE_MIGRATION_GUIDE.md)
- [智谱 AI 接入说明](docs/ZHIPU_API.md)
- [部署说明](docs/DEPLOY.md)

## License

MIT License