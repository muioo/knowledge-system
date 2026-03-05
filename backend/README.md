# 知识系统后端

基于 FastAPI 构建的知识管理系统后端 API。

## 功能特性

- 用户认证与授权（JWT）
- 多角色权限管理（管理员/普通用户）
- 文章 CRUD 与多标签关联
- 多格式文档上传并转换为 Markdown
- 文章搜索（标题/内容）与标签过滤
- 阅读历史与统计分析

## 技术栈

- FastAPI 0.104.1
- Tortoise ORM 0.20.0
- MySQL 8.0+
- JWT 认证
- Pydantic v2

## 目录结构

```bash
backend/
├── api/                    # API路由层
│   └── v1/                # API版本1
│       └── endpoints/     # 具体的端点模块
│           ├── auth/      # 认证相关接口
│           ├── users/     # 用户管理接口
│           ├── articles/  # 文章管理接口
│           ├── tags/      # 标签管理接口
│           ├── search/    # 搜索接口
│           └── reading/   # 阅读记录接口
├── controllers/           # 业务逻辑控制器层
├── core/                  # 核心功能模块
│   ├── security.py       # JWT认证、用户身份验证
│   ├── crud.py           # 通用CRUD操作基类
│   ├── dependencies.py   # FastAPI依赖注入函数
│   └── middleware.py     # 中间件（请求日志、错误处理）
├── models/               # 数据库模型层
├── schemas/              # 数据验证和序列化层
├── settings/             # 配置管理
│   └── config.py        # 应用配置、数据库配置等
├── utils/               # 工具函数库
│   ├── converters/      # 文档转换器
│   ├── jwt.py          # JWT令牌生成和解析
│   └── password.py     # 密码加密和验证
├── tests/              # 测试文件
├── docs/               # 文档
├── main.py            # 应用入口文件
└── requirements.txt   # 项目依赖
```

## 快速开始

### 1. 安装依赖

```bash
# 创建 conda 虚拟环境
conda create -n knowledge-system python=3.11
conda activate knowledge-system

# 安装项目依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置必要的配置项：

```env
# 应用配置
APP_NAME=知识系统后端
APP_VERSION=1.0.0
DEBUG=true
SECRET_KEY=your-secret-key-here

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your-database-password
DB_NAME=knowledge-system

# JWT 配置
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256

# 文件上传配置
MAX_FILE_SIZE=10485760
UPLOAD_DIR=./uploads

# CORS 配置
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

### 3. 初始化数据库

```bash
# 创建数据库（MySQL）
mysql -u root -p
CREATE DATABASE `knowledge-system` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 启动服务

```bash
# 开发环境（支持热重载）
uvicorn main:app --reload

# 生产环境
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. 访问 API 文档

启动服务后，可以通过以下地址访问自动生成的 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API 端点

### 认证相关 (`/api/v1/auth`)

- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/logout` - 用户登出
- `POST /api/v1/auth/refresh` - 刷新令牌

### 用户管理 (`/api/v1/users`)

- `GET /api/v1/users/` - 获取用户列表
- `GET /api/v1/users/{user_id}` - 获取用户详情
- `PUT /api/v1/users/{user_id}` - 更新用户信息
- `DELETE /api/v1/users/{user_id}` - 删除用户
- `PUT /api/v1/users/{user_id}/password` - 修改密码

### 文章管理 (`/api/v1/articles`)

- `GET /api/v1/articles/` - 获取文章列表
- `GET /api/v1/articles/{article_id}` - 获取文章详情
- `POST /api/v1/articles/` - 创建文章
- `PUT /api/v1/articles/{article_id}` - 更新文章
- `DELETE /api/v1/articles/{article_id}` - 删除文章
- `POST /api/v1/articles/upload` - 上传文档

### 标签管理 (`/api/v1/tags`)

- `GET /api/v1/tags/` - 获取标签列表
- `GET /api/v1/tags/{tag_id}` - 获取标签详情
- `POST /api/v1/tags/` - 创建标签
- `PUT /api/v1/tags/{tag_id}` - 更新标签
- `DELETE /api/v1/tags/{tag_id}` - 删除标签

### 搜索 (`/api/v1/search`)

- `GET /api/v1/search/articles` - 搜索文章
- `GET /api/v1/search/tags` - 搜索标签

### 阅读记录 (`/api/v1/reading`)

- `GET /api/v1/reading/history` - 获取阅读历史
- `POST /api/v1/reading/history/{article_id}` - 添加阅读记录
- `GET /api/v1/reading/stats` - 获取阅读统计
- `GET /api/v1/reading/progress/{article_id}` - 获取阅读进度
- `PUT /api/v1/reading/progress/{article_id}` - 更新阅读进度

## 支持的文档格式

系统支持将以下格式的文档自动转换为 Markdown：

- Word 文档 (`.docx`, `.doc`)
- PDF 文档 (`.pdf`)
- PowerPoint 演示文稿 (`.pptx`, `.ppt`)
- Markdown 文档 (`.md`, `.markdown`)
- HTML 文档 (`.html`, `.htm`)

## 开发指南

### 代码规范

项目遵循以下编码规范：

- 使用函数式、声明式编程
- 优先使用迭代和模块化，避免代码重复
- 使用带有辅助动词的描述性变量名（例如 `is_active`、`has_permission`）
- 目录和文件使用小写字母和下划线
- 优先处理错误和边缘情况
- 使用异步函数优化 I/O 密集型任务

### 测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_integration.py

# 运行测试并生成覆盖率报告
pytest --cov=. --cov-report=html
```

## 常见问题

### 数据库连接失败

检查 `.env` 文件中的数据库配置是否正确，确保 MySQL 服务正在运行。

### JWT 令牌过期

默认访问令牌有效期为 30 分钟，刷新令牌有效期为 7 天。可以在 `.env` 文件中调整这些配置。

### 文件上传失败

检查文件大小是否超过限制（默认 10MB），确保上传目录具有写入权限。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
