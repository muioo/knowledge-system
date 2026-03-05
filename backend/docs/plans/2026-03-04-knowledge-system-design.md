# 知识系统后端设计文档

**日期**: 2026-03-04
**版本**: 1.0
**技术栈**: FastAPI + Tortoise ORM + MySQL

---

## 1. 项目概述

### 1.1 项目目标
构建一个功能完善的知识管理系统后端，支持用户管理、文章管理、标签系统、全文搜索和阅读统计。

### 1.2 核心功能
- 用户认证与授权（JWT）
- 多角色权限管理（管理员/普通用户）
- 文章 CRUD 与多标签关联
- 多格式文档上传并转换为 Markdown
- 文章搜索（标题/内容）与标签过滤
- 阅读历史与统计分析

---

## 2. 技术选型

| 组件 | 技术方案 | 说明 |
|------|---------|------|
| Web 框架 | FastAPI 0.104.1 | 高性能异步框架 |
| 数据库 | MySQL 8.0+ | 关系型数据库 |
| ORM | Tortoise ORM 0.20.0 | 异步 ORM |
| 认证 | JWT (python-jose) | 无状态认证 |
| 密码加密 | bcrypt | 安全哈希 |
| 文档转换 | python-docx, pdfplumber, python-pptx, html2text | 多格式转 Markdown |

---

## 3. 数据模型设计

### 3.1 users 表 - 用户信息
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
);
```

### 3.2 articles 表 - 文章
```sql
CREATE TABLE articles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    original_filename VARCHAR(255),
    author_id INT NOT NULL,
    view_count INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_title (title),
    INDEX idx_author (author_id),
    FULLTEXT INDEX ft_search (title, content)
);
```

### 3.3 tags 表 - 标签
```sql
CREATE TABLE tags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    color VARCHAR(7) DEFAULT '#3498db',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_name (name)
);
```

### 3.4 article_tags 表 - 文章标签关联
```sql
CREATE TABLE article_tags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    article_id INT NOT NULL,
    tag_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    UNIQUE KEY uk_article_tag (article_id, tag_id)
);
```

### 3.5 reading_history 表 - 阅读历史
```sql
CREATE TABLE reading_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    article_id INT NOT NULL,
    started_at DATETIME NOT NULL,
    ended_at DATETIME,
    reading_duration INT DEFAULT 0 COMMENT '阅读时长(秒)',
    reading_progress INT DEFAULT 0 COMMENT '阅读进度(0-100)',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    INDEX idx_user_article (user_id, article_id),
    INDEX idx_started_at (started_at)
);
```

### 3.6 reading_stats 表 - 阅读统计
```sql
CREATE TABLE reading_stats (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    article_id INT NOT NULL,
    total_views INT DEFAULT 1,
    total_duration INT DEFAULT 0 COMMENT '总阅读时长(秒)',
    last_read_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_article (user_id, article_id),
    INDEX idx_user (user_id),
    INDEX idx_article (article_id)
);
```

---

## 4. API 端点设计

### 4.1 认证模块 (`/api/v1/auth`)

| 方法 | 端点 | 描述 | 权限 |
|------|------|------|------|
| POST | `/register` | 用户注册 | 公开 |
| POST | `/login` | 用户登录 | 公开 |
| POST | `/refresh` | 刷新令牌 | 公开 |
| POST | `/logout` | 登出 | 认证用户 |

### 4.2 用户管理 (`/api/v1/users`)

| 方法 | 端点 | 描述 | 权限 |
|------|------|------|------|
| GET | `/me` | 当前用户信息 | 认证用户 |
| PUT | `/me` | 更新当前用户 | 认证用户 |
| DELETE | `/me` | 删除当前用户 | 认证用户 |
| GET | `/` | 用户列表（分页） | 管理员 |
| GET | `/{user_id}` | 获取指定用户 | 管理员 |
| PUT | `/{user_id}` | 更新指定用户 | 管理员 |
| DELETE | `/{user_id}` | 删除指定用户 | 管理员 |
| PATCH | `/{user_id}/role` | 修改用户角色 | 管理员 |

### 4.3 文章管理 (`/api/v1/articles`)

| 方法 | 端点 | 描述 | 权限 |
|------|------|------|------|
| GET | `/` | 文章列表（分页） | 认证用户 |
| GET | `/{id}` | 获取文章详情 | 认证用户 |
| POST | `/` | 创建文章 | 认证用户 |
| PUT | `/{id}` | 更新文章 | 作者/管理员 |
| DELETE | `/{id}` | 删除文章 | 作者/管理员 |
| POST | `/upload` | 上传文档转 Markdown | 认证用户 |

### 4.4 标签管理 (`/api/v1/tags`)

| 方法 | 端点 | 描述 | 权限 |
|------|------|------|------|
| GET | `/` | 标签列表 | 公开 |
| POST | `/` | 创建标签 | 认证用户 |
| PUT | `/{id}` | 更新标签 | 认证用户 |
| DELETE | `/{id}` | 删除标签 | 认证用户 |
| GET | `/{id}/articles` | 获取标签下的文章 | 公开 |

### 4.5 搜索 (`/api/v1/search`)

| 方法 | 端点 | 描述 | 权限 |
|------|------|------|------|
| GET | `/articles` | 搜索文章 | 认证用户 |

**查询参数**:
- `q`: 搜索关键词（标题/内容）
- `tags`: 标签 ID 列表（逗号分隔）
- `page`: 页码（默认 1）
- `size`: 每页数量（默认 20）

### 4.6 阅读记录 (`/api/v1/reading`)

| 方法 | 端点 | 描述 | 权限 |
|------|------|------|------|
| POST | `/articles/{article_id}/start` | 开始阅读 | 认证用户 |
| POST | `/articles/{article_id}/end` | 结束阅读 | 认证用户 |
| GET | `/history` | 我的阅读历史 | 认证用户 |
| GET | `/stats` | 我的阅读统计 | 认证用户 |
| GET | `/articles/{article_id}/stats` | 文章阅读统计 | 管理员 |

---

## 5. 目录结构

```
backend/
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       └── endpoints/
│           ├── auth/
│           │   ├── __init__.py
│           │   └── router.py
│           ├── users/
│           │   ├── __init__.py
│           │   └── router.py
│           ├── articles/
│           │   ├── __init__.py
│           │   └── router.py
│           ├── tags/
│           │   ├── __init__.py
│           │   └── router.py
│           ├── search/
│           │   ├── __init__.py
│           │   └── router.py
│           └── reading/
│               ├── __init__.py
│               └── router.py
│
├── controllers/
│   ├── __init__.py
│   ├── auth_controller.py
│   ├── user_controller.py
│   ├── article_controller.py
│   ├── tag_controller.py
│   ├── search_controller.py
│   └── reading_controller.py
│
├── core/
│   ├── __init__.py
│   ├── security.py
│   ├── crud.py
│   ├── dependencies.py
│   └── middleware.py
│
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── article.py
│   ├── tag.py
│   └── reading.py
│
├── schemas/
│   ├── __init__.py
│   ├── user.py
│   ├── article.py
│   ├── tag.py
│   ├── reading.py
│   └── response.py
│
├── settings/
│   ├── __init__.py
│   └── config.py
│
├── utils/
│   ├── __init__.py
│   ├── password.py
│   ├── jwt.py
│   └── converters/
│       ├── __init__.py
│       ├── base.py
│       ├── word_converter.py
│       ├── pdf_converter.py
│       ├── ppt_converter.py
│       ├── md_converter.py
│       └── html_converter.py
│
├── main.py
├── requirements.txt
└── .env.example
```

---

## 6. 核心功能实现

### 6.1 文档转换流程

```
上传文件
    ↓
验证文件类型和大小
    ↓
选择对应转换器
    ↓
提取文本 + 转换为 Markdown
    ↓
提取标题（作为文章标题）
    ↓
保存到数据库
    ↓
返回文章信息
```

### 6.2 认证授权

**JWT 令牌配置**:
- 访问令牌有效期: 30 分钟
- 刷新令牌有效期: 7 天
- 算法: HS256

**权限矩阵**:

| 功能 | 普通用户 | 管理员 |
|------|---------|--------|
| 登录/注册 | ✅ | ✅ |
| 管理自己的账户 | ✅ | ✅ |
| 管理自己的文章 | ✅ | ✅ |
| 管理所有用户 | ❌ | ✅ |
| 管理所有文章 | ❌ | ✅ |
| 查看全局统计 | ❌ | ✅ |

### 6.3 搜索实现

**Phase 1（当前实现）**: MySQL LIKE 搜索
```python
Q(title__icontains=keyword) | Q(content__icontains=keyword)
```

**Phase 2（预留扩展）**: Elasticsearch 接口预留

### 6.4 阅读统计

**统计逻辑**:
- 每次阅读结束更新 `reading_stats`
- 累加 `total_views` 和 `total_duration`
- 记录 `last_read_at`

---

## 7. 响应格式

### 7.1 成功响应
```json
{
    "code": 200,
    "message": "success",
    "data": {...}
}
```

### 7.2 分页响应
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "total": 100,
        "page": 1,
        "size": 20,
        "items": [...]
    }
}
```

### 7.3 错误响应
```json
{
    "code": 400,
    "message": "错误描述",
    "detail": {...}
}
```

---

## 8. 配置说明

### 8.1 数据库配置
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=123456
DB_NAME=knowledge-system
```

### 8.2 应用配置
```env
APP_NAME=知识系统后端
DEBUG=True
SECRET_KEY=your-secret-key
MAX_FILE_SIZE=10485760
UPLOAD_DIR=./uploads
```

---

## 9. 安全考虑

1. **密码安全**: 使用 bcrypt 加密存储
2. **JWT 安全**: 密钥从环境变量读取，令牌有过期时间
3. **SQL 注入**: 使用 ORM 参数化查询
4. **文件上传**: 验证文件类型和大小
5. **CORS**: 限制允许的跨域来源
6. **权限控制**: 基于角色的访问控制（RBAC）

---

## 10. 后续优化方向

1. **搜索升级**: 集成 Elasticsearch 实现高性能全文搜索
2. **缓存优化**: 使用 Redis 缓存热门文章
3. **异步任务**: 使用 Celery 处理大文件转换
4. **日志系统**: 集成结构化日志（如 ELK）
5. **监控告警**: 集成 Prometheus + Grafana
