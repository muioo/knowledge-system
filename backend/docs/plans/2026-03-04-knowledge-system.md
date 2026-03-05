# 知识系统后端实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 构建一个完整的知识管理系统后端，支持用户认证、文章管理、标签系统、搜索和阅读统计。

**架构:** 采用单体模块化架构，FastAPI + Tortoise ORM + MySQL，函数式编程风格，按功能模块分层（API层、Controller层、Model层、Schema层）。

**技术栈:** FastAPI 0.104.1, Tortoise ORM 0.20.0, MySQL, JWT (python-jose), Pydantic v2

---

## 前置准备

### Task 0: 项目初始化

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `main.py`
- Create: `.gitignore`

**Step 1: 创建 requirements.txt**

```txt
# Web 框架
fastapi==0.104.1
uvicorn[standard]==0.24.0

# 数据库
tortoise-orm==0.20.0
aiomysql==0.2.0
asyncmy==0.0.21

# 认证
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# 验证
pydantic==2.5.0
pydantic-settings==2.1.0
email-validator==2.1.0

# 文档转换
python-docx==1.1.0
pdfplumber==0.10.3
python-pptx==0.6.23
html2text==2020.1.16
markdown==3.5.1

# 工具
python-dotenv==1.0.0
aiofiles==23.2.1
```

**Step 2: 创建 .env.example**

```env
# 应用配置
APP_NAME=知识系统后端
APP_VERSION=1.0.0
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=123456
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

**Step 3: 创建 .gitignore**

```
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
ENV/
env/
.env
*.db
*.sqlite3
uploads/
*.log
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
.DS_Store
```

**Step 4: 创建基础 main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="知识系统后端", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

**Step 5: 测试启动**

```bash
# 创建虚拟环境
conda create -n knowledge-system python=3.11
conda activate knowledge-system

# 安装依赖
pip install -r requirements.txt

# 测试启动
uvicorn main:app --reload
```

**Step 6: 提交**

```bash
git add requirements.txt .env.example main.py .gitignore
git commit -m "chore: initialize project with dependencies and basic setup"
```

---

## 阶段一：配置与核心模块

### Task 1: 配置管理模块

**Files:**
- Create: `settings/__init__.py`
- Create: `settings/config.py`
- Create: `tests/test_config.py`

**Step 1: 创建配置模型**

`settings/config.py`:

```python
from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # 应用配置
    app_name: str = "知识系统后端"
    app_version: str = "1.0.0"
    debug: bool = True
    secret_key: str

    # 数据库配置
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str
    db_name: str = "knowledge-system"

    # JWT 配置
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    algorithm: str = "HS256"

    # 文件上传配置
    max_file_size: int = 10485760  # 10MB
    upload_dir: str = "./uploads"

    # CORS 配置
    cors_origins: str = '["http://localhost:3000", "http://localhost:8000"]'

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.cors_origins)

    @property
    def database_url(self) -> str:
        return f"mysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
```

**Step 2: 创建测试**

`tests/test_config.py`:

```python
import pytest
from settings.config import settings


def test_settings_load():
    assert settings.app_name == "知识系统后端"
    assert settings.app_version == "1.0.0"


def test_database_url():
    db_url = settings.database_url
    assert "mysql://" in db_url
    assert "knowledge-system" in db_url


def test_cors_origins_list():
    origins = settings.cors_origins_list
    assert isinstance(origins, list)
    assert "http://localhost:3000" in origins
```

**Step 3: 运行测试**

```bash
pytest tests/test_config.py -v
```

**Step 4: 提交**

```bash
git add settings/ tests/test_config.py
git commit -m "feat: add configuration management module"
```

---

### Task 2: 数据库模型

**Files:**
- Create: `models/__init__.py`
- Create: `models/user.py`
- Create: `models/article.py`
- Create: `models/tag.py`
- Create: `models/reading.py`
- Create: `tests/test_models.py`

**Step 1: 创建用户模型**

`models/user.py`:

```python
from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=100, unique=True)
    hashed_password = fields.CharField(max_length=255)
    role = fields.CharField(max_length=10, default="user")  # admin, user
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"

    def __str__(self):
        return self.username
```

**Step 2: 创建文章模型**

`models/article.py`:

```python
from tortoise import fields
from tortoise.models import Model


class Article(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    original_filename = fields.CharField(max_length=255, null=True)
    author = fields.ForeignKeyField("models.User", related_name="articles", on_delete=fields.CASCADE)
    view_count = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    tags: fields.ManyToManyRelation["Tag"] = fields.ManyToManyField(
        "models.Tag", related_name="articles", through="article_tags"
    )

    class Meta:
        table = "articles"

    def __str__(self):
        return self.title
```

**Step 3: 创建标签模型**

`models/tag.py`:

```python
from tortoise import fields
from tortoise.models import Model


class Tag(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)
    color = fields.CharField(max_length=7, default="#3498db")
    created_at = fields.DatetimeField(auto_now_add=True)

    articles: fields.ManyToManyRelation[Article] = fields.ManyToManyField(
        "models.Article", related_name="tags", through="article_tags"
    )

    class Meta:
        table = "tags"

    def __str__(self):
        return self.name
```

**Step 4: 创建阅读记录模型**

`models/reading.py`:

```python
from tortoise import fields
from tortoise.models import Model


class ReadingHistory(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="reading_histories", on_delete=fields.CASCADE)
    article = fields.ForeignKeyField("models.Article", related_name="reading_histories", on_delete=fields.CASCADE)
    started_at = fields.DatetimeField()
    ended_at = fields.DatetimeField(null=True)
    reading_duration = fields.IntField(default=0)  # 秒
    reading_progress = fields.IntField(default=0)  # 0-100

    class Meta:
        table = "reading_history"

    def __str__(self):
        return f"{self.user_id} - {self.article_id}"


class ReadingStats(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="reading_stats", on_delete=fields.CASCADE)
    article = fields.ForeignKeyField("models.Article", related_name="reading_stats", on_delete=fields.CASCADE)
    total_views = fields.IntField(default=1)
    total_duration = fields.IntField(default=0)  # 秒
    last_read_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "reading_stats"
        unique_together = (("user", "article"),)

    def __str__(self):
        return f"{self.user_id} - {self.article_id} stats"
```

**Step 5: 注册所有模型**

`models/__init__.py`:

```python
from tortoise import Tortoise
from models.user import User
from models.article import Article
from models.tag import Tag
from models.reading import ReadingHistory, ReadingStats

TORTOISE_ORM = {
    "connections": {"default": "mysql://root:123456@localhost:3306/knowledge-system"},
    "apps": {
        "models": {
            "models": ["models.user", "models.article", "models.tag", "models.reading"],
            "default_connection": "default",
        }
    },
}

__all__ = ["User", "Article", "Tag", "ReadingHistory", "ReadingStats", "TORTOISE_ORM"]
```

**Step 6: 创建测试**

`tests/test_models.py`:

```python
import pytest
from tortoise import Tortoise
from models import User, Article, Tag, ReadingHistory, ReadingStats, TORTOISE_ORM


@pytest.fixture
async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest.mark.asyncio
async def test_create_user(init_db):
    user = await User.create(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed"
    )
    assert user.id is not None
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_user_role_default(init_db):
    user = await User.create(
        username="testuser2",
        email="test2@example.com",
        hashed_password="hashed"
    )
    assert user.role == "user"
```

**Step 7: 运行测试**

```bash
pytest tests/test_models.py -v
```

**Step 8: 提交**

```bash
git add models/ tests/test_models.py
git commit -m "feat: add database models (user, article, tag, reading)"
```

---

### Task 3: 核心安全模块

**Files:**
- Create: `core/__init__.py`
- Create: `core/security.py`
- Create: `utils/__init__.py`
- Create: `utils/password.py`
- Create: `utils/jwt.py`
- Create: `tests/test_security.py`

**Step 1: 创建密码工具**

`utils/password.py`:

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

**Step 2: 创建 JWT 工具**

`utils/jwt.py`:

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from settings.config import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None
```

**Step 3: 创建安全依赖**

`core/security.py`:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models import User
from utils.jwt import decode_token

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(credentials.credentials)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = await User.get_or_none(id=int(user_id))
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")

    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    return current_user
```

**Step 4: 创建测试**

`tests/test_security.py`:

```python
import pytest
from utils.password import hash_password, verify_password
from utils.jwt import create_access_token, decode_token


def test_hash_password():
    password = "test123"
    hashed = hash_password(password)
    assert hashed != password
    assert len(hashed) > 50


def test_verify_password():
    password = "test123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_create_access_token():
    data = {"sub": "1", "role": "user"}
    token = create_access_token(data)
    assert token is not None
    assert isinstance(token, str)


def test_decode_token():
    data = {"sub": "1", "role": "user"}
    token = create_access_token(data)
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "1"
```

**Step 5: 运行测试**

```bash
pytest tests/test_security.py -v
```

**Step 6: 提交**

```bash
git add core/ utils/ tests/test_security.py
git commit -m "feat: add security module (password hashing, JWT, auth dependencies)"
```

---

## 阶段二：Pydantic Schemas

### Task 4: 用户 Schemas

**Files:**
- Create: `schemas/__init__.py`
- Create: `schemas/user.py`
- Create: `schemas/response.py`
- Create: `tests/test_schemas.py`

**Step 1: 创建用户 Schemas**

`schemas/user.py`:

```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=50)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=50)


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class UpdateRole(BaseModel):
    role: str = Field(..., pattern="^(admin|user)$")
```

**Step 2: 创建通用响应 Schema**

`schemas/response.py`:

```python
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: T


class PaginatedResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: "PaginatedData[T]"


class PaginatedData(BaseModel, Generic[T]):
    total: int
    page: int
    size: int
    items: list[T]


class ErrorResponse(BaseModel):
    code: int
    message: str
    detail: Optional[dict] = None
```

**Step 3: 创建测试**

`tests/test_schemas.py`:

```python
import pytest
from schemas.user import UserCreate, UserUpdate, UserResponse


def test_user_create_valid():
    user = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    assert user.username == "testuser"


def test_user_create_invalid_password():
    with pytest.raises(ValueError):
        UserCreate(
            username="testuser",
            email="test@example.com",
            password="123"  # 太短
        )


def test_user_update_partial():
    user = UserUpdate(email="new@example.com")
    assert user.email == "new@example.com"
    assert user.password is None
```

**Step 4: 运行测试**

```bash
pytest tests/test_schemas.py -v
```

**Step 5: 提交**

```bash
git add schemas/ tests/test_schemas.py
git commit -m "feat: add user schemas and response models"
```

---

### Task 5: 文章和标签 Schemas

**Files:**
- Create: `schemas/article.py`
- Create: `schemas/tag.py`
- Modify: `tests/test_schemas.py`

**Step 1: 创建文章 Schemas**

`schemas/article.py`:

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class ArticleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str


class ArticleCreate(ArticleBase):
    tag_ids: Optional[List[int]] = []


class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    tag_ids: Optional[List[int]] = None


class TagInfo(BaseModel):
    id: int
    name: str
    color: str

    class Config:
        from_attributes = True


class ArticleResponse(ArticleBase):
    id: int
    author_id: int
    original_filename: Optional[str] = None
    view_count: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagInfo] = []

    class Config:
        from_attributes = True


class ArticleUploadResponse(BaseModel):
    id: int
    title: str
    content: str
    original_filename: str


class SearchQuery(BaseModel):
    q: Optional[str] = None
    tags: Optional[List[int]] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
```

**Step 2: 创建标签 Schemas**

`schemas/tag.py`:

```python
from pydantic import BaseModel, Field
from datetime import datetime


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#3498db", pattern=r"^#[0-9A-Fa-f]{6}$")


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: str = Field(None, min_length=1, max_length=50)
    color: str = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class TagResponse(TagBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
```

**Step 3: 创建阅读记录 Schemas**

`schemas/reading.py`:

```python
from pydantic import BaseModel, Field
from datetime import datetime


class ReadingStart(BaseModel):
    pass


class ReadingEnd(BaseModel):
    reading_progress: int = Field(default=0, ge=0, le=100)


class ReadingHistoryResponse(BaseModel):
    id: int
    article_id: int
    article_title: str
    started_at: datetime
    ended_at: datetime = None
    reading_duration: int
    reading_progress: int


class ReadingStatsResponse(BaseModel):
    article_id: int
    article_title: str
    total_views: int
    total_duration: int
    last_read_at: datetime
```

**Step 4: 提交**

```bash
git add schemas/ tests/test_schemas.py
git commit -m "feat: add article, tag and reading schemas"
```

---

## 阶段三：业务逻辑控制器

### Task 6: 认证控制器

**Files:**
- Create: `controllers/__init__.py`
- Create: `controllers/auth_controller.py`
- Create: `tests/test_auth_controller.py`

**Step 1: 创建认证控制器**

`controllers/auth_controller.py`:

```python
from models import User
from schemas.user import UserCreate, TokenResponse, UserResponse
from utils.password import hash_password, verify_password
from utils.jwt import create_access_token, create_refresh_token
from typing import Optional


async def register_user(data: UserCreate) -> UserResponse:
    # 检查用户名是否存在
    existing = await User.get_or_none(username=data.username)
    if existing:
        raise ValueError("用户名已存在")

    # 检查邮箱是否存在
    existing = await User.get_or_none(email=data.email)
    if existing:
        raise ValueError("邮箱已被使用")

    # 创建用户
    hashed = hash_password(data.password)
    user = await User.create(
        username=data.username,
        email=data.email,
        hashed_password=hashed
    )

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )


async def authenticate_user(username: str, password: str) -> Optional[User]:
    user = await User.get_or_none(username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def login_user(username: str, password: str) -> TokenResponse:
    user = await authenticate_user(username, password)
    if not user:
        raise ValueError("用户名或密码错误")

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
    )
```

**Step 2: 创建测试**

`tests/test_auth_controller.py`:

```python
import pytest
from tortoise import Tortoise
from models import User, TORTOISE_ORM
from controllers.auth_controller import register_user, authenticate_user
from schemas.user import UserCreate


@pytest.fixture
async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest.mark.asyncio
async def test_register_user(init_db):
    data = UserCreate(
        username="newuser",
        email="new@example.com",
        password="password123"
    )
    user = await register_user(data)
    assert user.username == "newuser"
    assert user.role == "user"


@pytest.mark.asyncio
async def test_register_duplicate_username(init_db):
    data = UserCreate(
        username="dupuser",
        email="dup@example.com",
        password="password123"
    )
    await register_user(data)
    with pytest.raises(ValueError, match="用户名已存在"):
        await register_user(data)


@pytest.mark.asyncio
async def test_authenticate_user(init_db):
    data = UserCreate(
        username="authuser",
        email="auth@example.com",
        password="password123"
    )
    await register_user(data)

    user = await authenticate_user("authuser", "password123")
    assert user is not None
    assert user.username == "authuser"

    user = await authenticate_user("authuser", "wrongpass")
    assert user is None
```

**Step 3: 运行测试**

```bash
pytest tests/test_auth_controller.py -v
```

**Step 4: 提交**

```bash
git add controllers/ tests/test_auth_controller.py
git commit -m "feat: add authentication controller (register, login)"
```

---

### Task 7: 用户控制器

**Files:**
- Create: `controllers/user_controller.py`
- Create: `tests/test_user_controller.py`

**Step 1: 创建用户控制器**

`controllers/user_controller.py`:

```python
from models import User
from schemas.user import UserResponse, UserUpdate, UpdateRole
from typing import List


async def get_user_by_id(user_id: int) -> UserResponse:
    user = await User.get_or_none(id=user_id)
    if not user:
        raise ValueError("用户不存在")
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )


async def update_user(user_id: int, data: UserUpdate) -> UserResponse:
    user = await User.get_or_none(id=user_id)
    if not user:
        raise ValueError("用户不存在")

    if data.email:
        user.email = data.email
    if data.password:
        from utils.password import hash_password
        user.hashed_password = hash_password(data.password)

    await user.save()

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )


async def delete_user(user_id: int) -> bool:
    user = await User.get_or_none(id=user_id)
    if not user:
        raise ValueError("用户不存在")
    await user.delete()
    return True


async def list_users(page: int = 1, size: int = 20) -> tuple[List[UserResponse], int]:
    total = await User.all().count()
    users = await User.all().offset((page - 1) * size).limit(size)

    return (
        [
            UserResponse(
                id=u.id,
                username=u.username,
                email=u.email,
                role=u.role,
                is_active=u.is_active,
                created_at=u.created_at
            ) for u in users
        ],
        total
    )


async def update_user_role(user_id: int, data: UpdateRole) -> UserResponse:
    user = await User.get_or_none(id=user_id)
    if not user:
        raise ValueError("用户不存在")

    user.role = data.role
    await user.save()

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )
```

**Step 2: 提交**

```bash
git add controllers/user_controller.py tests/test_user_controller.py
git commit -m "feat: add user controller (CRUD operations)"
```

---

### Task 8: 文章控制器

**Files:**
- Create: `controllers/article_controller.py`
- Create: `tests/test_article_controller.py`

**Step 1: 创建文章控制器**

`controllers/article_controller.py`:

```python
from models import Article, Tag
from schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse, SearchQuery
from schemas.tag import TagInfo
from typing import List, Optional
from tortoise.queryset import Q


async def create_article(data: ArticleCreate, author_id: int) -> ArticleResponse:
    article = await Article.create(
        title=data.title,
        content=data.content,
        author_id=author_id
    )

    if data.tag_ids:
        tags = await Tag.filter(id__in=data.tag_ids)
        await article.tags.add(*tags)

    await article.fetch_related("tags")

    return ArticleResponse(
        id=article.id,
        title=article.title,
        content=article.content,
        author_id=article.author_id,
        original_filename=article.original_filename,
        view_count=article.view_count,
        created_at=article.created_at,
        updated_at=article.updated_at,
        tags=[TagInfo(id=t.id, name=t.name, color=t.color) for t in article.tags]
    )


async def get_article_by_id(article_id: int) -> ArticleResponse:
    article = await Article.get_or_none(id=article_id).prefetch_related("tags")
    if not article:
        raise ValueError("文章不存在")

    # 增加阅读次数
    article.view_count += 1
    await article.save()

    return ArticleResponse(
        id=article.id,
        title=article.title,
        content=article.content,
        author_id=article.author_id,
        original_filename=article.original_filename,
        view_count=article.view_count,
        created_at=article.created_at,
        updated_at=article.updated_at,
        tags=[TagInfo(id=t.id, name=t.name, color=t.color) for t in article.tags]
    )


async def update_article(article_id: int, data: ArticleUpdate, user_id: int, is_admin: bool = False) -> ArticleResponse:
    article = await Article.get_or_none(id=article_id).prefetch_related("tags")
    if not article:
        raise ValueError("文章不存在")

    if article.author_id != user_id and not is_admin:
        raise ValueError("无权编辑此文章")

    if data.title:
        article.title = data.title
    if data.content:
        article.content = data.content

    await article.save()

    if data.tag_ids is not None:
        await article.tags.clear()
        tags = await Tag.filter(id__in=data.tag_ids)
        await article.tags.add(*tags)
        await article.fetch_related("tags")

    return ArticleResponse(
        id=article.id,
        title=article.title,
        content=article.content,
        author_id=article.author_id,
        original_filename=article.original_filename,
        view_count=article.view_count,
        created_at=article.created_at,
        updated_at=article.updated_at,
        tags=[TagInfo(id=t.id, name=t.name, color=t.color) for t in article.tags]
    )


async def delete_article(article_id: int, user_id: int, is_admin: bool = False) -> bool:
    article = await Article.get_or_none(id=article_id)
    if not article:
        raise ValueError("文章不存在")

    if article.author_id != user_id and not is_admin:
        raise ValueError("无权删除此文章")

    await article.delete()
    return True


async def list_articles(page: int = 1, size: int = 20, tag_id: Optional[int] = None, author_id: Optional[int] = None) -> tuple[List[ArticleResponse], int]:
    query = Article.all()

    if tag_id:
        query = query.filter(tags__id=tag_id)

    if author_id:
        query = query.filter(author_id=author_id)

    total = await query.count()
    articles = await query.prefetch_related("tags").offset((page - 1) * size).limit(size)

    return (
        [
            ArticleResponse(
                id=a.id,
                title=a.title,
                content=a.content,
                author_id=a.author_id,
                original_filename=a.original_filename,
                view_count=a.view_count,
                created_at=a.created_at,
                updated_at=a.updated_at,
                tags=[TagInfo(id=t.id, name=t.name, color=t.color) for t in a.tags]
            ) for a in articles
        ],
        total
    )


async def search_articles(query: SearchQuery) -> tuple[List[ArticleResponse], int]:
    articles_query = Article.all()

    if query.q:
        articles_query = articles_query.filter(
            Q(title__icontains=query.q) | Q(content__icontains=query.q)
        )

    if query.tags:
        articles_query = articles_query.filter(tags__id__in=query.tags)

    total = await articles_query.count()
    articles = await articles_query.prefetch_related("tags").distinct().offset(
        (query.page - 1) * query.size
    ).limit(query.size)

    return (
        [
            ArticleResponse(
                id=a.id,
                title=a.title,
                content=a.content,
                author_id=a.author_id,
                original_filename=a.original_filename,
                view_count=a.view_count,
                created_at=a.created_at,
                updated_at=a.updated_at,
                tags=[TagInfo(id=t.id, name=t.name, color=t.color) for t in a.tags]
            ) for a in articles
        ],
        total
    )
```

**Step 2: 提交**

```bash
git add controllers/article_controller.py tests/test_article_controller.py
git commit -m "feat: add article controller (CRUD, search)"
```

---

### Task 9: 标签和阅读控制器

**Files:**
- Create: `controllers/tag_controller.py`
- Create: `controllers/reading_controller.py`

**Step 1: 创建标签控制器**

`controllers/tag_controller.py`:

```python
from models import Tag, Article
from schemas.tag import TagCreate, TagUpdate, TagResponse
from schemas.article import ArticleResponse, TagInfo
from typing import List, Optional


async def create_tag(data: TagCreate) -> TagResponse:
    existing = await Tag.get_or_none(name=data.name)
    if existing:
        raise ValueError("标签已存在")

    tag = await Tag.create(name=data.name, color=data.color)
    return TagResponse(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        created_at=tag.created_at
    )


async def get_tag_by_id(tag_id: int) -> TagResponse:
    tag = await Tag.get_or_none(id=tag_id)
    if not tag:
        raise ValueError("标签不存在")

    return TagResponse(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        created_at=tag.created_at
    )


async def list_tags() -> List[TagResponse]:
    tags = await Tag.all()
    return [
        TagResponse(
            id=t.id,
            name=t.name,
            color=t.color,
            created_at=t.created_at
        ) for t in tags
    ]


async def update_tag(tag_id: int, data: TagUpdate) -> TagResponse:
    tag = await Tag.get_or_none(id=tag_id)
    if not tag:
        raise ValueError("标签不存在")

    if data.name:
        tag.name = data.name
    if data.color:
        tag.color = data.color

    await tag.save()

    return TagResponse(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        created_at=tag.created_at
    )


async def delete_tag(tag_id: int) -> bool:
    tag = await Tag.get_or_none(id=tag_id)
    if not tag:
        raise ValueError("标签不存在")

    await tag.delete()
    return True


async def get_articles_by_tag(tag_id: int, page: int = 1, size: int = 20) -> tuple[List[ArticleResponse], int]:
    tag = await Tag.get_or_none(id=tag_id)
    if not tag:
        raise ValueError("标签不存在")

    total = await tag.articles.all().count()
    articles = await tag.articles.all().prefetch_related("tags").offset((page - 1) * size).limit(size)

    return (
        [
            ArticleResponse(
                id=a.id,
                title=a.title,
                content=a.content,
                author_id=a.author_id,
                original_filename=a.original_filename,
                view_count=a.view_count,
                created_at=a.created_at,
                updated_at=a.updated_at,
                tags=[TagInfo(id=t.id, name=t.name, color=t.color) for t in a.tags]
            ) for a in articles
        ],
        total
    )
```

**Step 2: 创建阅读控制器**

`controllers/reading_controller.py`:

```python
from models import ReadingHistory, ReadingStats, Article
from schemas.reading import ReadingEnd, ReadingHistoryResponse, ReadingStatsResponse
from datetime import datetime
from typing import List


async def start_reading(user_id: int, article_id: int) -> ReadingHistoryResponse:
    article = await Article.get_or_none(id=article_id)
    if not article:
        raise ValueError("文章不存在")

    history = await ReadingHistory.create(
        user_id=user_id,
        article_id=article_id,
        started_at=datetime.now()
    )

    return ReadingHistoryResponse(
        id=history.id,
        article_id=article.id,
        article_title=article.title,
        started_at=history.started_at,
        ended_at=history.ended_at,
        reading_duration=history.reading_duration,
        reading_progress=history.reading_progress
    )


async def end_reading(user_id: int, article_id: int, data: ReadingEnd) -> ReadingHistoryResponse:
    history = await ReadingHistory.filter(
        user_id=user_id,
        article_id=article_id
    ).order_by("-started_at").first()

    if not history:
        raise ValueError("没有找到阅读记录")

    history.ended_at = datetime.now()
    history.reading_progress = data.reading_progress
    history.reading_duration = int((history.ended_at - history.started_at).total_seconds())
    await history.save()

    # 更新统计
    stats, created = await ReadingStats.get_or_create(
        user_id=user_id,
        article_id=article_id,
        defaults={
            "total_views": 1,
            "total_duration": history.reading_duration
        }
    )

    if not created:
        stats.total_views += 1
        stats.total_duration += history.reading_duration
        await stats.save()

    article = await Article.get(id=article_id)

    return ReadingHistoryResponse(
        id=history.id,
        article_id=article.id,
        article_title=article.title,
        started_at=history.started_at,
        ended_at=history.ended_at,
        reading_duration=history.reading_duration,
        reading_progress=history.reading_progress
    )


async def get_reading_history(user_id: int, page: int = 1, size: int = 20) -> tuple[List[ReadingHistoryResponse], int]:
    total = await ReadingHistory.filter(user_id=user_id).count()
    histories = await ReadingHistory.filter(
        user_id=user_id
    ).order_by("-started_at").prefetch_related("article").offset((page - 1) * size).limit(size)

    return (
        [
            ReadingHistoryResponse(
                id=h.id,
                article_id=h.article_id,
                article_title=h.article.title,
                started_at=h.started_at,
                ended_at=h.ended_at,
                reading_duration=h.reading_duration,
                reading_progress=h.reading_progress
            ) for h in histories
        ],
        total
    )


async def get_reading_stats(user_id: int, page: int = 1, size: int = 20) -> tuple[List[ReadingStatsResponse], int]:
    total = await ReadingStats.filter(user_id=user_id).count()
    stats = await ReadingStats.filter(
        user_id=user_id
    ).order_by("-last_read_at").prefetch_related("article").offset((page - 1) * size).limit(size)

    return (
        [
            ReadingStatsResponse(
                article_id=s.article_id,
                article_title=s.article.title,
                total_views=s.total_views,
                total_duration=s.total_duration,
                last_read_at=s.last_read_at
            ) for s in stats
        ],
        total
    )


async def get_article_reading_stats(article_id: int, page: int = 1, size: int = 20) -> tuple[List[ReadingStatsResponse], int]:
    article = await Article.get_or_none(id=article_id)
    if not article:
        raise ValueError("文章不存在")

    total = await ReadingStats.filter(article_id=article_id).count()
    stats = await ReadingStats.filter(
        article_id=article_id
    ).order_by("-total_views").prefetch_related("article", "user").offset((page - 1) * size).limit(size)

    return (
        [
            ReadingStatsResponse(
                article_id=s.article_id,
                article_title=s.article.title,
                total_views=s.total_views,
                total_duration=s.total_duration,
                last_read_at=s.last_read_at
            ) for s in stats
        ],
        total
    )
```

**Step 3: 提交**

```bash
git add controllers/tag_controller.py controllers/reading_controller.py
git commit -m "feat: add tag and reading controllers"
```

---

## 阶段四：文档转换模块

### Task 10: 文档转换器

**Files:**
- Create: `utils/converters/__init__.py`
- Create: `utils/converters/base.py`
- Create: `utils/converters/word_converter.py`
- Create: `utils/converters/pdf_converter.py`
- Create: `utils/converters/ppt_converter.py`
- Create: `utils/converters/md_converter.py`
- Create: `utils/converters/html_converter.py`
- Create: `tests/test_converters.py`

**Step 1: 创建转换器基类**

`utils/converters/base.py`:

```python
from abc import ABC, abstractmethod
from pathlib import Path


class BaseConverter(ABC):
    """文档转换器基类"""

    @classmethod
    @abstractmethod
    def supports(cls, filename: str) -> bool:
        """检查是否支持该文件类型"""
        pass

    @classmethod
    @abstractmethod
    async def convert(cls, file_path: str) -> tuple[str, str]:
        """
        转换文件为 Markdown
        返回: (markdown_content, extracted_title)
        """
        pass
```

**Step 2: 创建 Word 转换器**

`utils/converters/word_converter.py`:

```python
from docx import Document
from .base import BaseConverter
import asyncio


class WordConverter(BaseConverter):
    @classmethod
    def supports(cls, filename: str) -> bool:
        return filename.lower().endswith((".docx", ".doc"))

    @classmethod
    async def convert(cls, file_path: str) -> tuple[str, str]:
        def _convert():
            doc = Document(file_path)
            lines = []

            # 提取标题（第一个段落）
            title = "未命名文档"
            if doc.paragraphs:
                first_para = doc.paragraphs[0].text.strip()
                if first_para:
                    title = first_para
                    lines.append(f"# {title}\n")

            # 提取正文
            for para in doc.paragraphs[1:]:
                text = para.text.strip()
                if text:
                    lines.append(text)

            # 提取表格
            for table in doc.tables:
                lines.append("\n| " + " | ".join([cell.text for cell in table.rows[0].cells]) + " |")
                lines.append("| " + " | ".join(["---" for _ in table.rows[0].cells]) + " |")
                for row in table.rows[1:]:
                    lines.append("| " + " | ".join([cell.text for cell in row.cells]) + " |")

            return "\n\n".join(lines), title

        return await asyncio.get_event_loop().run_in_executor(None, _convert)
```

**Step 3: 创建 PDF 转换器**

`utils/converters/pdf_converter.py`:

```python
import pdfplumber
from .base import BaseConverter
import asyncio


class PDFConverter(BaseConverter):
    @classmethod
    def supports(cls, filename: str) -> bool:
        return filename.lower().endswith(".pdf")

    @classmethod
    async def convert(cls, file_path: str) -> tuple[str, str]:
        def _convert():
            content = []
            title = "未命名文档"

            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        content.append(text.strip())
                        # 第一页的第一行作为标题
                        if i == 0 and content:
                            first_line = text.strip().split("\n")[0]
                            if first_line:
                                title = first_line

            markdown = "\n\n".join(content)
            return markdown, title

        return await asyncio.get_event_loop().run_in_executor(None, _convert)
```

**Step 4: 创建 PPT 转换器**

`utils/converters/ppt_converter.py`:

```python
from pptx import Presentation
from .base import BaseConverter
import asyncio


class PPTConverter(BaseConverter):
    @classmethod
    def supports(cls, filename: str) -> bool:
        return filename.lower().endswith((".pptx", ".ppt"))

    @classmethod
    async def convert(cls, file_path: str) -> tuple[str, str]:
        def _convert():
            prs = Presentation(file_path)
            content = []
            title = "未命名演示"

            for i, slide in enumerate(prs.slides):
                slide_content = []

                # 提取标题
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        slide_content.append(shape.text.strip())
                        if i == 0 and not title:
                            title = shape.text.strip()
                            break

                if slide_content:
                    content.append(f"\n## 幻灯片 {i + 1}\n")
                    content.extend(slide_content)

            return "\n".join(content), title

        return await asyncio.get_event_loop().run_in_executor(None, _convert)
```

**Step 5: 创建 Markdown 转换器**

`utils/converters/md_converter.py`:

```python
from .base import BaseConverter
import aiofiles


class MarkdownConverter(BaseConverter):
    @classmethod
    def supports(cls, filename: str) -> bool:
        return filename.lower().endswith((".md", ".markdown"))

    @classmethod
    async def convert(cls, file_path: str) -> tuple[str, str]:
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            content = await f.read()

        # 提取标题（第一个 # 标题）
        title = "未命名文档"
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("#"):
                title = line.lstrip("#").strip()
                break
            elif line:
                title = line
                break

        return content, title
```

**Step 6: 创建 HTML 转换器**

`utils/converters/html_converter.py`:

```python
import html2text
from .base import BaseConverter
import asyncio
from bs4 import BeautifulSoup


class HTMLConverter(BaseConverter):
    @classmethod
    def supports(cls, filename: str) -> bool:
        return filename.lower().endswith((".html", ".htm"))

    @classmethod
    async def convert(cls, file_path: str) -> tuple[str, str]:
        def _convert():
            with open(file_path, "r", encoding="utf-8") as f:
                html = f.read()

            # 提取标题
            soup = BeautifulSoup(html, "html.parser")
            title = "未命名文档"
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
            elif soup.h1:
                title = soup.h1.get_text().strip()

            # 转换为 Markdown
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            markdown = h.handle(html)

            return markdown.strip(), title

        return await asyncio.get_event_loop().run_in_executor(None, _convert)
```

**Step 7: 创建转换器工厂**

`utils/converters/__init__.py`:

```python
from .word_converter import WordConverter
from .pdf_converter import PDFConverter
from .ppt_converter import PPTConverter
from .md_converter import MarkdownConverter
from .html_converter import HTMLConverter
from typing import List

CONVERTERS: List[type] = [
    WordConverter,
    PDFConverter,
    PPTConverter,
    MarkdownConverter,
    HTMLConverter,
]


def get_converter(filename: str):
    """根据文件名获取合适的转换器"""
    for converter_class in CONVERTERS:
        if converter_class.supports(filename):
            return converter_class()
    raise ValueError(f"不支持的文件类型: {filename}")


async def convert_document(file_path: str, filename: str) -> tuple[str, str]:
    """转换文档为 Markdown"""
    converter = get_converter(filename)
    return await converter.convert(file_path)


__all__ = ["convert_document", "get_converter"]
```

**Step 8: 提交**

```bash
git add utils/converters/ tests/test_converters.py
git commit -m "feat: add document converters (Word, PDF, PPT, Markdown, HTML)"
```

---

## 阶段五：API 路由层

### Task 11: 认证路由

**Files:**
- Create: `api/__init__.py`
- Create: `api/v1/__init__.py`
- Create: `api/v1/endpoints/__init__.py`
- Create: `api/v1/endpoints/auth/__init__.py`
- Create: `api/v1/endpoints/auth/router.py`

**Step 1: 创建认证路由**

`api/v1/endpoints/auth/router.py`:

```python
from fastapi import APIRouter, HTTPException, status
from schemas.user import UserCreate, UserLogin, TokenResponse
from controllers.auth_controller import register_user, login_user
from schemas.response import SuccessResponse

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=SuccessResponse[TokenResponse])
async def register(data: UserCreate):
    try:
        result = await register_user(data)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=SuccessResponse[TokenResponse])
async def login(data: UserLogin):
    try:
        result = await login_user(data.username, data.password)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
```

**Step 2: 更新 main.py 注册路由**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from api.v1.endpoints.auth import router as auth_router
from models import TORTOISE_ORM
from settings.config import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册数据库
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)

# 注册路由
app.include_router(auth_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

**Step 3: 提交**

```bash
git add api/ main.py
git commit -m "feat: add authentication API routes (register, login)"
```

---

### Task 12: 用户路由

**Files:**
- Create: `api/v1/endpoints/users/__init__.py`
- Create: `api/v1/endpoints/users/router.py`

**Step 1: 创建用户路由**

`api/v1/endpoints/users/router.py`:

```python
from fastapi import APIRouter, HTTPException, Depends, status
from core.security import get_current_user, get_current_admin
from models import User
from schemas.user import UserResponse, UserUpdate, UpdateRole
from schemas.response import SuccessResponse, PaginatedResponse, PaginatedData
from controllers.user_controller import (
    get_user_by_id,
    update_user,
    delete_user,
    list_users,
    update_user_role
)

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/me", response_model=SuccessResponse[UserResponse])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return SuccessResponse(data=UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    ))


@router.put("/me", response_model=SuccessResponse[UserResponse])
async def update_current_user_info(
    data: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    try:
        result = await update_user(current_user.id, data)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/me", status_code=204)
async def delete_current_user(current_user: User = Depends(get_current_user)):
    try:
        await delete_user(current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=PaginatedResponse[UserResponse])
async def get_users(
    page: int = 1,
    size: int = 20,
    current_admin: User = Depends(get_current_admin)
):
    users, total = await list_users(page, size)
    return PaginatedResponse(data=PaginatedData(
        total=total,
        page=page,
        size=size,
        items=users
    ))


@router.get("/{user_id}", response_model=SuccessResponse[UserResponse])
async def get_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin)
):
    try:
        result = await get_user_by_id(user_id)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{user_id}", response_model=SuccessResponse[UserResponse])
async def update_user_by_id(
    user_id: int,
    data: UserUpdate,
    current_admin: User = Depends(get_current_admin)
):
    try:
        result = await update_user(user_id, data)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", status_code=204)
async def delete_user_by_id(
    user_id: int,
    current_admin: User = Depends(get_current_admin)
):
    try:
        await delete_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{user_id}/role", response_model=SuccessResponse[UserResponse])
async def update_user_role_by_id(
    user_id: int,
    data: UpdateRole,
    current_admin: User = Depends(get_current_admin)
):
    try:
        result = await update_user_role(user_id, data)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**Step 2: 更新 main.py 注册路由**

```python
# 在 main.py 中添加
from api.v1.endpoints.users import router as users_router

app.include_router(users_router, prefix="/api/v1")
```

**Step 3: 提交**

```bash
git add api/v1/endpoints/users/ main.py
git commit -m "feat: add user management API routes"
```

---

### Task 13: 文章路由

**Files:**
- Create: `api/v1/endpoints/articles/__init__.py`
- Create: `api/v1/endpoints/articles/router.py`

**Step 1: 创建文章路由**

`api/v1/endpoints/articles/router.py`:

```python
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import Optional
from core.security import get_current_user, get_current_admin
from models import User
from schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse
from schemas.response import SuccessResponse, PaginatedResponse, PaginatedData
from controllers.article_controller import (
    create_article,
    get_article_by_id,
    update_article,
    delete_article,
    list_articles
)
from utils.converters import convert_document
import aiofiles
import os
from settings.config import settings

router = APIRouter(prefix="/articles", tags=["文章"])


@router.get("/", response_model=PaginatedResponse[ArticleResponse])
async def get_articles(
    page: int = 1,
    size: int = 20,
    tag_id: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    articles, total = await list_articles(page, size, tag_id)
    return PaginatedResponse(data=PaginatedData(
        total=total,
        page=page,
        size=size,
        items=articles
    ))


@router.get("/{article_id}", response_model=SuccessResponse[ArticleResponse])
async def get_article(
    article_id: int,
    current_user: User = Depends(get_current_user)
):
    try:
        result = await get_article_by_id(article_id)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=SuccessResponse[ArticleResponse])
async def create_new_article(
    data: ArticleCreate,
    current_user: User = Depends(get_current_user)
):
    try:
        result = await create_article(data, current_user.id)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{article_id}", response_model=SuccessResponse[ArticleResponse])
async def update_article_by_id(
    article_id: int,
    data: ArticleUpdate,
    current_user: User = Depends(get_current_user)
):
    try:
        is_admin = current_user.role == "admin"
        result = await update_article(article_id, data, current_user.id, is_admin)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400 if "无权" in str(e) else 404, detail=str(e))


@router.delete("/{article_id}", status_code=204)
async def delete_article_by_id(
    article_id: int,
    current_user: User = Depends(get_current_user)
):
    try:
        is_admin = current_user.role == "admin"
        await delete_article(article_id, current_user.id, is_admin)
    except ValueError as e:
        raise HTTPException(status_code=403 if "无权" in str(e) else 404, detail=str(e))


@router.post("/upload", response_model=SuccessResponse[ArticleResponse])
async def upload_document(
    file: UploadFile = File(...),
    tag_ids: str = Form(None),
    current_user: User = Depends(get_current_user)
):
    # 验证文件大小
    content = await file.read()
    if len(content) > settings.max_file_size:
        raise HTTPException(status_code=413, detail="文件过大")

    # 保存文件
    os.makedirs(settings.upload_dir, exist_ok=True)
    file_path = os.path.join(settings.upload_dir, file.filename)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # 转换文档
    try:
        markdown_content, title = await convert_document(file_path, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=415, detail=str(e))

    # 创建文章
    tag_id_list = [int(t) for t in tag_ids.split(",")] if tag_ids else []
    article_data = ArticleCreate(
        title=title,
        content=markdown_content,
        tag_ids=tag_id_list
    )

    try:
        result = await create_article(article_data, current_user.id)
        # 更新原始文件名
        from models import Article
        article = await Article.get(id=result.id)
        article.original_filename = file.filename
        await article.save()
        result.original_filename = file.filename
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**Step 2: 更新 main.py 注册路由**

```python
from api.v1.endpoints.articles import router as articles_router

app.include_router(articles_router, prefix="/api/v1")
```

**Step 3: 提交**

```bash
git add api/v1/endpoints/articles/ main.py
git commit -m "feat: add article management API routes with document upload"
```

---

### Task 14: 标签、搜索和阅读路由

**Files:**
- Create: `api/v1/endpoints/tags/__init__.py`
- Create: `api/v1/endpoints/tags/router.py`
- Create: `api/v1/endpoints/search/__init__.py`
- Create: `api/v1/endpoints/search/router.py`
- Create: `api/v1/endpoints/reading/__init__.py`
- Create: `api/v1/endpoints/reading/router.py`

**Step 1: 创建标签路由**

`api/v1/endpoints/tags/router.py`:

```python
from fastapi import APIRouter, HTTPException, Depends
from core.security import get_current_user
from models import User
from schemas.tag import TagCreate, TagUpdate, TagResponse
from schemas.response import SuccessResponse
from controllers.tag_controller import (
    create_tag,
    get_tag_by_id,
    list_tags,
    update_tag,
    delete_tag,
    get_articles_by_tag
)
from schemas.article import ArticleResponse
from schemas.response import PaginatedResponse, PaginatedData

router = APIRouter(prefix="/tags", tags=["标签"])


@router.get("/", response_model=SuccessResponse[list[TagResponse]])
async def get_tags():
    tags = await list_tags()
    return SuccessResponse(data=tags)


@router.get("/{tag_id}", response_model=SuccessResponse[TagResponse])
async def get_tag(tag_id: int):
    try:
        result = await get_tag_by_id(tag_id)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=SuccessResponse[TagResponse])
async def create_new_tag(
    data: TagCreate,
    current_user: User = Depends(get_current_user)
):
    try:
        result = await create_tag(data)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{tag_id}", response_model=SuccessResponse[TagResponse])
async def update_tag_by_id(
    tag_id: int,
    data: TagUpdate,
    current_user: User = Depends(get_current_user)
):
    try:
        result = await update_tag(tag_id, data)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{tag_id}", status_code=204)
async def delete_tag_by_id(
    tag_id: int,
    current_user: User = Depends(get_current_user)
):
    try:
        await delete_tag(tag_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{tag_id}/articles", response_model=PaginatedResponse[ArticleResponse])
async def get_tag_articles(
    tag_id: int,
    page: int = 1,
    size: int = 20
):
    try:
        articles, total = await get_articles_by_tag(tag_id, page, size)
        return PaginatedResponse(data=PaginatedData(
            total=total,
            page=page,
            size=size,
            items=articles
        ))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

**Step 2: 创建搜索路由**

`api/v1/endpoints/search/router.py`:

```python
from fastapi import APIRouter, Depends, Query
from typing import Optional
from core.security import get_current_user
from models import User
from schemas.article import ArticleResponse
from schemas.response import PaginatedResponse, PaginatedData
from controllers.article_controller import search_articles

router = APIRouter(prefix="/search", tags=["搜索"])


@router.get("/articles", response_model=PaginatedResponse[ArticleResponse])
async def search_articles_endpoint(
    q: Optional[str] = None,
    tags: Optional[str] = Query(None, description="逗号分隔的标签ID"),
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user)
):
    tag_ids = [int(t) for t in tags.split(",")] if tags else None

    from schemas.article import SearchQuery
    query = SearchQuery(q=q, tags=tag_ids, page=page, size=size)

    articles, total = await search_articles(query)
    return PaginatedResponse(data=PaginatedData(
        total=total,
        page=page,
        size=size,
        items=articles
    ))
```

**Step 3: 创建阅读路由**

`api/v1/endpoints/reading/router.py`:

```python
from fastapi import APIRouter, HTTPException, Depends
from core.security import get_current_user, get_current_admin
from models import User
from schemas.reading import ReadingEnd, ReadingHistoryResponse, ReadingStatsResponse
from schemas.response import SuccessResponse, PaginatedResponse, PaginatedData
from controllers.reading_controller import (
    start_reading,
    end_reading,
    get_reading_history,
    get_reading_stats,
    get_article_reading_stats
)

router = APIRouter(prefix="/reading", tags=["阅读记录"])


@router.post("/articles/{article_id}/start", response_model=SuccessResponse[ReadingHistoryResponse])
async def start_reading_article(
    article_id: int,
    current_user: User = Depends(get_current_user)
):
    try:
        result = await start_reading(current_user.id, article_id)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/articles/{article_id}/end", response_model=SuccessResponse[ReadingHistoryResponse])
async def end_reading_article(
    article_id: int,
    data: ReadingEnd,
    current_user: User = Depends(get_current_user)
):
    try:
        result = await end_reading(current_user.id, article_id, data)
        return SuccessResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history", response_model=PaginatedResponse[ReadingHistoryResponse])
async def get_my_reading_history(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user)
):
    histories, total = await get_reading_history(current_user.id, page, size)
    return PaginatedResponse(data=PaginatedData(
        total=total,
        page=page,
        size=size,
        items=histories
    ))


@router.get("/stats", response_model=PaginatedResponse[ReadingStatsResponse])
async def get_my_reading_stats(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user)
):
    stats, total = await get_reading_stats(current_user.id, page, size)
    return PaginatedResponse(data=PaginatedData(
        total=total,
        page=page,
        size=size,
        items=stats
    ))


@router.get("/articles/{article_id}/stats", response_model=PaginatedResponse[ReadingStatsResponse])
async def get_article_stats(
    article_id: int,
    page: int = 1,
    size: int = 20,
    current_admin: User = Depends(get_current_admin)
):
    try:
        stats, total = await get_article_reading_stats(article_id, page, size)
        return PaginatedResponse(data=PaginatedData(
            total=total,
            page=page,
            size=size,
            items=stats
        ))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

**Step 4: 更新 main.py 注册所有路由**

```python
from api.v1.endpoints.tags import router as tags_router
from api.v1.endpoints.search import router as search_router
from api.v1.endpoints.reading import router as reading_router

app.include_router(tags_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(reading_router, prefix="/api/v1")
```

**Step 5: 提交**

```bash
git add api/v1/endpoints/tags/ api/v1/endpoints/search/ api/v1/endpoints/reading/ main.py
git commit -m "feat: add tag, search and reading API routes"
```

---

## 阶段六：中间件和错误处理

### Task 15: 中间件和错误处理

**Files:**
- Create: `core/middleware.py`
- Modify: `main.py`

**Step 1: 创建中间件**

`core/middleware.py`:

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # 记录请求
        logger.info(f"请求: {request.method} {request.url.path}")

        response = await call_next(request)

        # 记录响应时间
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(f"响应: {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"错误: {request.method} {request.url.path} - {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "code": 500,
                    "message": "服务器内部错误",
                    "detail": {"error": str(e)} if request.app.debug else None
                }
            )
```

**Step 2: 更新 main.py 添加中间件**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from core.middleware import RequestLoggingMiddleware, ErrorHandlingMiddleware
from api.v1.endpoints.auth import router as auth_router
from api.v1.endpoints.users import router as users_router
from api.v1.endpoints.articles import router as articles_router
from api.v1.endpoints.tags import router as tags_router
from api.v1.endpoints.search import router as search_router
from api.v1.endpoints.reading import router as reading_router
from models import TORTOISE_ORM
from settings.config import settings

app = FastAPI(title=settings.app_name, version=settings.app_version, debug=settings.debug)

# 添加中间件
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册数据库
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)

# 注册路由
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(articles_router, prefix="/api/v1")
app.include_router(tags_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(reading_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Step 3: 提交**

```bash
git add core/middleware.py main.py
git commit -m "feat: add logging and error handling middleware"
```

---

## 完成检查

### Task 16: 最终测试和文档

**Files:**
- Create: `README.md`
- Create: `tests/test_integration.py`

**Step 1: 创建 README.md**

```markdown
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

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
conda create -n knowledge-system python=3.11
conda activate knowledge-system

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

### 3. 启动服务

```bash
uvicorn main:app --reload
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 认证
- POST `/api/v1/auth/register` - 用户注册
- POST `/api/v1/auth/login` - 用户登录

### 用户管理
- GET `/api/v1/users/me` - 当前用户信息
- GET `/api/v1/users` - 用户列表（管理员）

### 文章管理
- GET `/api/v1/articles` - 文章列表
- POST `/api/v1/articles` - 创建文章
- POST `/api/v1/articles/upload` - 上传文档

### 标签管理
- GET `/api/v1/tags` - 标签列表
- POST `/api/v1/tags` - 创建标签

### 搜索
- GET `/api/v1/search/articles` - 搜索文章

### 阅读记录
- POST `/api/v1/reading/articles/{id}/start` - 开始阅读
- GET `/api/v1/reading/history` - 阅读历史

## 开发

### 运行测试

```bash
pytest tests/ -v
```

### 代码风格

遵循项目 `CLAUDE.md` 中的编码规范。
```

**Step 2: 创建集成测试**

`tests/test_integration.py`:

```python
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_register_login_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 注册
        response = await client.post("/api/v1/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 200

        # 登录
        response = await client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "password123"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()["data"]


@pytest.mark.asyncio
async def test_create_article_with_tags():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 先登录获取 token
        login_response = await client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "password123"
        })
        token = login_response.json()["data"]["access_token"]

        headers = {"Authorization": f"Bearer {token}"}

        # 创建标签
        tag_response = await client.post("/api/v1/tags", json={
            "name": "Python",
            "color": "#3498db"
        }, headers=headers)
        assert tag_response.status_code == 200
        tag_id = tag_response.json()["data"]["id"]

        # 创建文章
        article_response = await client.post("/api/v1/articles", json={
            "title": "测试文章",
            "content": "这是一篇测试文章",
            "tag_ids": [tag_id]
        }, headers=headers)
        assert article_response.status_code == 200
```

**Step 3: 运行所有测试**

```bash
pytest tests/ -v --cov=.
```

**Step 4: 最终提交**

```bash
git add README.md tests/test_integration.py
git commit -m "docs: add README and integration tests"
```

---

## 实现完成

完成所有任务后，系统应该具备：

1. ✅ 完整的用户认证与授权系统
2. ✅ 基于角色的权限控制
3. ✅ 文章 CRUD 操作
4. ✅ 多标签关联功能
5. ✅ 文档上传与转换
6. ✅ 文章搜索功能
7. ✅ 阅读记录与统计
8. ✅ 统一的错误处理和响应格式
9. ✅ API 文档自动生成

### 可选后续优化

- [ ] 集成 Redis 缓存
- [ ] 集成 Elasticsearch 实现高性能搜索
- [ ] 添加单元测试覆盖率报告
- [ ] 集成 CI/CD 流程
- [ ] 添加 Docker 支持
