---
author: muioo
title: "【Claude Code 规则】FastAPI 后端开发规则"
date: 2026-01-26
description: "FastAPI 可扩展 API 开发的核心规则、目录结构及实践指南"
tags: ["FastAPI", "Python", "后端开发", "claude code 规则设计"]
categories: ["开发技术"]
---

# 后端开发规则（fastapi）

- 您是一位精通 Python、FastAPI 和可扩展 API 开发的专家。

## 关键原则

- 编写简洁、技术性的回复，并提供准确的 Python 示例。
- 使用函数式、声明式编程；尽可能避免使用类。
- 优先使用迭代和模块化，避免代码重复。
- 使用带有辅助动词的描述性变量名（例如 `is_active`、`has_permission`）。
- 目录和文件使用小写字母和下划线（例如 `article_controller.py`）。
- 优先使用命名导出路由和工具函数。
- 使用"接收对象，返回对象"（RORO）模式。

## 项目结构

### 完整目录树

```
backend/
├── api/                              # API 路由层
│   ├── __init__.py
│   └── v1/                           # API 版本 1
│       ├── __init__.py               # 注册所有 v1 路由
│       └── endpoints/                # 具体端点模块
│           ├── __init__.py
│           ├── auth/                 # 认证相关接口
│           │   ├── __init__.py
│           │   └── router.py         # 登录、注册、刷新token
│           ├── users/                # 用户管理接口
│           │   ├── __init__.py
│           │   └── router.py         # 用户CRUD、角色管理
│           ├── articles/             # 文章管理接口
│           │   ├── __init__.py
│           │   └── router.py         # 文章CRUD、上传、URL导入
│           ├── tags/                 # 标签管理接口
│           │   ├── __init__.py
│           │   └── router.py         # 标签CRUD、文章关联
│           ├── search/               # 搜索接口
│           │   ├── __init__.py
│           │   └── router.py         # 文章搜索
│           ├── reading/              # 阅读记录接口
│           │   ├── __init__.py
│           │   └── router.py         # 阅读历史、统计
│           └── media/                # 媒体文件接口
│               ├── __init__.py
│               └── router.py         # 图片、HTML文件访问
├── controllers/                      # 业务逻辑控制器层
│   ├── __init__.py
│   ├── auth_controller.py            # 认证业务逻辑
│   ├── user_controller.py            # 用户管理业务逻辑
│   ├── article_controller.py         # 文章管理业务逻辑
│   ├── tag_controller.py             # 标签管理业务逻辑
│   └── reading_controller.py         # 阅读记录业务逻辑
├── core/                             # 核心功能模块
│   ├── __init__.py
│   ├── security.py                   # JWT认证、依赖注入
│   └── middleware.py                 # 中间件（日志、错误处理）
├── models/                           # 数据库模型层
│   ├── __init__.py                   # 导出所有模型
│   ├── user.py                       # 用户模型
│   ├── article.py                    # 文章模型
│   ├── tag.py                        # 标签模型
│   └── reading.py                    # 阅读历史和统计模型
├── schemas/                          # Pydantic 数据验证层
│   ├── __init__.py
│   ├── response.py                   # 通用响应模式
│   ├── user.py                       # 用户相关模式
│   ├── article.py                    # 文章相关模式
│   ├── tag.py                        # 标签相关模式
│   └── reading.py                    # 阅读记录相关模式
├── settings/                         # 配置管理
│   ├── __init__.py
│   └── config.py                     # 应用配置（使用 Pydantic Settings）
├── utils/                            # 工具函数库
│   ├── __init__.py
│   ├── jwt.py                        # JWT 令牌生成和解析
│   ├── password.py                   # 密码加密和验证
│   ├── article_storage.py            # 文章文件存储管理
│   ├── ai_extractor.py               # AI 提取文章信息（火山引擎）
│   ├── html_fetcher.py               # HTML 获取和处理
│   ├── image_processor.py            # 图片提取、下载和处理
│   └── converters/                   # 文档转换器
│       ├── __init__.py               # 转换器工厂
│       ├── base.py                   # 转换器基类
│       ├── html_converter.py         # HTML 转换器
│       ├── md_converter.py           # Markdown 转换器
│       ├── pdf_converter.py          # PDF 转换器
│       ├── ppt_converter.py          # PowerPoint 转换器
│       └── word_converter.py         # Word 转换器
├── tests/                            # 测试文件
│   ├── test_integration.py           # 集成测试
│   ├── test_config.py                # 配置测试
│   ├── test_models.py                # 模型测试
│   ├── test_security.py              # 安全测试
│   ├── test_article_controller_integration.py  # 文章控制器集成测试
│   ├── test_article_storage.py       # 文章存储测试
│   └── test_html_article.py          # HTML 文章测试
├── docs/                             # 文档目录
├── uploads/                          # 文件上传目录
├── main.py                           # 应用入口文件
├── create_admin.py                   # 创建管理员脚本
├── requirements.txt                  # 项目依赖
├── README.md                         # 项目说明文档
└── CLAUDE.md                         # 后端开发规则（本项目特有）
```

### 分层架构说明

```
┌─────────────────────────────────────────┐
│           API 路由层          │  ← HTTP 请求入口
│   - 参数验证                              │
│   - 权限检查                              │
│   - 响应封装                              │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      业务逻辑控制器层     │  ← 业务逻辑处理
│   - 业务规则验证                          │
│   - 数据处理                              │
│   - 事务管理                              │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│       工具函数层                 │  ← 可复用逻辑
│   - JWT 管理                              │
│   - 文件处理                              │
│   - 数据转换                              │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│     数据访问层          │  ← 数据库交互
│   - CRUD 操作                              │
│   - 关系管理                              │
│   - 查询优化                              │
└─────────────────────────────────────────┘
```

## API 规范

### 路由设计规范

#### 1. 路由注册模式

统一在 `api/v1/__init__.py` 中注册所有路由：

```python
def register_routers(app: FastAPI):
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(articles_router, prefix="/api/v1")
    app.include_router(tags_router, prefix="/api/v1")
    app.include_router(search_router, prefix="/api/v1")
    app.include_router(reading_router, prefix="/api/v1")
    app.include_router(media_router, prefix="/api/v1")
```

#### 2. 路由定义规范

```python
from fastapi import APIRouter

router = APIRouter(prefix="/articles", tags=["文章"])

@router.get("/", response_model=PaginatedResponse[ArticleResponse])
async def list_articles(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user)
):
    """获取文章列表"""
    pass
```

#### 3. RESTful 风格

| 操作 | HTTP 方法 | 路径 | 说明 |
|------|-----------|------|------|
| 列表 | GET | `/articles` | 获取文章列表 |
| 详情 | GET | `/articles/{id}` | 获取单篇文章 |
| 创建 | POST | `/articles` | 创建新文章 |
| 更新 | PUT | `/articles/{id}` | 更新文章 |
| 删除 | DELETE | `/articles/{id}` | 删除文章 |

### 响应格式规范

#### 1. 统一响应结构

所有 API 响应都使用统一的包装格式：

```python
# 成功响应
class SuccessResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: T

# 分页响应
class PaginatedResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: PaginatedData[T]

class PaginatedData(BaseModel, Generic[T]):
    total: int      # 总数
    page: int       # 当前页
    size: int       # 每页大小
    items: list[T]  # 数据列表
```

#### 2. 错误响应格式

```python
# 错误响应
{
    "code": 400,           # HTTP 状态码
    "message": "错误描述",
    "detail": {            # 可选，仅在 debug 模式
        "error": "详细错误信息"
    }
}
```

### 认证和授权

#### 1. JWT 认证

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """获取当前登录用户"""
    token = credentials.credentials
    payload = decode_token(token)
    user = await User.get_or_none(id=payload["user_id"])
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user
```

#### 2. 权限验证

```python
async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """验证管理员权限"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    return current_user
```

#### 3. 使用示例

```python
# 公开接口
@router.post("/register")
async def register(data: UserRegister):
    pass

# 需要登录
@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    pass

# 需要管理员
@router.delete("/users/{id}")
async def delete_user(id: int, admin: User = Depends(get_current_admin)):
    pass
```

## 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件/目录 | 小写字母 + 下划线 | `article_controller.py` |
| 类名 | 大驼峰（PascalCase） | `User`, `ArticleResponse` |
| 函数名 | 小写字母 + 下划线 | `get_article_by_id` |
| 变量名 | 小写字母 + 下划线 | `article_id`, `user_name` |
| 常量 | 大写字母 + 下划线 | `MAX_FILE_SIZE` |
| 私有函数 | 下划线前缀 | `_clean_text()` |

## 代码风格

### Python/FastAPI

- 使用 `def` 定义纯函数，使用 `async def` 定义异步操作
- 为所有函数签名使用类型提示
- 优先使用 Pydantic 模型进行输入验证
- 使用文档字符串（docstring）说明函数功能

```python
async def create_article(
    data: ArticleCreate,
    author_id: int,
    file_data: Optional[tuple[bytes, str]] = None
) -> ArticleResponse:
    """
    创建新文章

    Args:
        data: 文章创建数据
        author_id: 作者 ID
        file_data: 可选的文件数据 (内容, 文件名)

    Returns:
        创建的文章响应

    Raises:
        ValueError: 数据验证失败
    """
    pass
```

### 错误处理

- 优先处理错误和边缘情况
- 使用提前返回避免深度嵌套
- 使用守卫子句处理前提条件
- 所有错误都需要记录日志

```python
async def get_article(article_id: int) -> ArticleResponse:
    # 守卫子句：验证输入
    if article_id <= 0:
        raise ValueError("无效的文章 ID")

    # 尝试获取数据
    article = await Article.get_or_none(id=article_id)
    if not article:
        raise ValueError(f"文章 {article_id} 不存在")

    # 正常路径
    return ArticleResponse.from_orm(article)
```

## 数据库操作

### TortoiseORM 使用

#### 1. 基本操作

```python
# 创建
article = await Article.create(
    title="标题",
    summary="摘要",
    author_id=author_id
)

# 查询
article = await Article.get_or_none(id=article_id)
articles = await Article.all().offset((page-1)*size).limit(size)

# 更新
article.title = "新标题"
await article.save()

# 删除
await article.delete()
```

#### 2. 关系操作

```python
# 多对多 - 添加
tags = await Tag.filter(id__in=tag_ids)
await article.tags.add(*tags)

# 多对多 - 清除
await article.tags.clear()

# 预加载关系
await article.fetch_related("tags")
articles = await query.prefetch_related("tags")
```

#### 3. 复杂查询

```python
from tortoise.expressions import Q

# OR 查询
articles = await Article.filter(
    Q(title__icontains=query) |
    Q(summary__icontains=query)
)

# IN 查询
articles = await Article.filter(tags__id__in=tag_ids)

# 去重
articles = await articles.distinct()
```

### 配置管理

数据库配置统一在 `settings/config.py` 中管理：

```python
class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str
    db_name: str = "knowledge-system"

    @property
    def tortoise_orm(self) -> dict:
        """TortoiseORM 配置"""
        return {
            "connections": {"default": self.database_url},
            "apps": {
                "models": {
                    "models": [
                        "backend.models.user",
                        "backend.models.article",
                        "backend.models.tag",
                        "backend.models.reading"
                    ],
                    "default_connection": "default",
                }
            },
            "use_tz": False,
            "timezone": "Asia/Shanghai"
        }
```

## 性能优化

### 1. 异步优先

所有 I/O 操作使用异步：

```python
# ✅ 正确 - 异步
async def save_article(content: str):
    async with aiofiles.open("file.html", "w") as f:
        await f.write(content)

# ❌ 错误 - 同步
def save_article(content: str):
    with open("file.html", "w") as f:
        f.write(content)
```

### 2. 查询优化

```python
# 使用预加载避免 N+1 查询
articles = await Article.all().prefetch_related("tags")

# 使用 select_related 预加载外键
articles = await Article.all().select_related("author")
```

### 3. 分页

所有列表接口必须支持分页：

```python
async def list_articles(page: int = 1, size: int = 20):
    offset = (page - 1) * size
    items = await Article.all().offset(offset).limit(size)
    total = await Article.all().count()
    return items, total
```

## 关键约定

1. **依赖注入**：使用 FastAPI 的依赖注入系统管理状态
2. **类型安全**：所有函数必须有完整的类型提示
3. **错误日志**：所有错误必须记录日志
4. **配置隔离**：数据库配置只在 `settings/config.py` 中定义
5. **异步优先**：所有 I/O 操作使用异步
6. **响应统一**：所有 API 使用统一的响应格式

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| Web 框架 | FastAPI | 0.104.1 |
| ORM | TortoiseORM | 0.25.4 |
| 数据验证 | Pydantic | 2.5.0 |
| 数据库 | MySQL | 8.0+ |
| 认证 | JWT (python-jose) | 3.3.0 |
| 密码加密 | passlib (bcrypt) | 1.7.4 |

## 虚拟环境

- 采用 conda 虚拟环境
- 环境名称：`knowledge-system`