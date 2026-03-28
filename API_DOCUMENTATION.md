# 知识系统后端 API 接口文档

> 版本: v1
> 基础路径: `/api/v1`
> 文档生成时间: 2025-03-07

## 目录

- [基础信息](#基础信息)
- [认证方式](#认证方式)
- [通用响应格式](#通用响应格式)
- [认证模块](#认证模块)
- [用户模块](#用户模块)
- [文章模块](#文章模块)
- [标签模块](#标签模块)
- [搜索模块](#搜索模块)
- [阅读记录模块](#阅读记录模块)
- [数据模型](#数据模型)

---

## 基础信息

### 环境配置

```yaml
开发环境: http://localhost:8022
API版本: v1
数据格式: JSON
字符编码: UTF-8
```

### 通用请求头

```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer {access_token}
```

---

## 认证方式

### JWT Token 认证

所有需要认证的接口都需要在请求头中携带 JWT Token：

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token 有效期**
- Access Token: 7 天
- Refresh Token: 30 天

### 权限说明

- **普通用户 (user)**: 可以访问个人资源、创建/编辑自己的文章
- **管理员 (admin)**: 拥有所有权限，可以管理用户、查看所有数据

---

## 通用响应格式

### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

### 分页响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "size": 20,
    "items": [ ... ]
  }
}
```

### 错误响应

```json
{
  "detail": "错误信息描述"
}
```

**常见 HTTP 状态码**
- `200`: 成功
- `201`: 创建成功
- `204`: 成功（无返回内容）
- `400`: 请求参数错误
- `401`: 未认证
- `403`: 无权限
- `404`: 资源不存在
- `409`: 资源冲突
- `413`: 文件过大
- `422`: 参数验证失败

---

## 认证模块

### 用户注册

```http
POST /api/v1/auth/register
```

**请求体**

```json
{
  "username": "string (3-50字符)",
  "email": "string (邮箱格式)",
  "password": "string (6-50字符)"
}
```

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "role": "user",
      "is_active": true,
      "created_at": "2025-03-07T10:00:00Z"
    }
  }
}
```

### 用户登录

```http
POST /api/v1/auth/login
```

**请求体**

```json
{
  "username": "string",
  "password": "string"
}
```

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "role": "user",
      "is_active": true,
      "created_at": "2025-03-07T10:00:00Z"
    }
  }
}
```

**错误响应**

- `401`: 用户名或密码错误

---

## 用户模块

### 获取当前用户信息

```http
GET /api/v1/users/me
```

**需要认证**: ✅

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2025-03-07T10:00:00Z"
  }
}
```

### 更新当前用户信息

```http
PUT /api/v1/users/me
```

**需要认证**: ✅

**请求体**

```json
{
  "email": "string (可选, 邮箱格式)",
  "password": "string (可选, 6-50字符)"
}
```

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "newemail@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2025-03-07T10:00:00Z"
  }
}
```

### 删除当前用户

```http
DELETE /api/v1/users/me
```

**需要认证**: ✅

**响应**: `204 No Content`

### 获取用户列表（管理员）

```http
GET /api/v1/users/?page=1&size=20
```

**需要认证**: ✅ (管理员权限)

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认 1 |
| size | integer | 否 | 每页数量，默认 20 |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "size": 20,
    "items": [
      {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "role": "user",
        "is_active": true,
        "created_at": "2025-03-07T10:00:00Z"
      }
    ]
  }
}
```

### 获取指定用户（管理员）

```http
GET /api/v1/users/{user_id}
```

**需要认证**: ✅ (管理员权限)

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| user_id | integer | 用户ID |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2025-03-07T10:00:00Z"
  }
}
```

### 更新指定用户（管理员）

```http
PUT /api/v1/users/{user_id}
```

**需要认证**: ✅ (管理员权限)

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| user_id | integer | 用户ID |

**请求体**

```json
{
  "email": "string (可选)",
  "password": "string (可选, 6-50字符)"
}
```

### 删除指定用户（管理员）

```http
DELETE /api/v1/users/{user_id}
```

**需要认证**: ✅ (管理员权限)

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| user_id | integer | 用户ID |

**响应**: `204 No Content`

### 更新用户角色（管理员）

```http
PATCH /api/v1/users/{user_id}/role
```

**需要认证**: ✅ (管理员权限)

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| user_id | integer | 用户ID |

**请求体**

```json
{
  "role": "admin 或 user"
}
```

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "admin",
    "is_active": true,
    "created_at": "2025-03-07T10:00:00Z"
  }
}
```

---

## 文章模块

### 获取文章列表

```http
GET /api/v1/articles/?page=1&size=20&tag_id=1
```

**需要认证**: ✅

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认 1 |
| size | integer | 否 | 每页数量，默认 20 |
| tag_id | integer | 否 | 按标签筛选 |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "size": 20,
    "items": [
      {
        "id": 1,
        "title": "文章标题",
        "source_url": "https://example.com",
        "summary": "文章摘要",
        "keywords": "关键词1,关键词2",
        "author_id": 1,
        "original_filename": "article.html",
        "view_count": 100,
        "created_at": "2025-03-07T10:00:00Z",
        "updated_at": "2025-03-07T10:00:00Z",
        "tags": [
          {
            "id": 1,
            "name": "技术",
            "color": "#3498db"
          }
        ],
        "html_content": null,
        "html_path": "articles/1/index.html",
        "processing_status": "completed",
        "original_html_url": "https://example.com/original"
      }
    ]
  }
}
```

### 获取文章详情

```http
GET /api/v1/articles/{article_id}
```

**需要认证**: ✅

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| article_id | integer | 文章ID |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "文章标题",
    "source_url": "https://example.com",
    "summary": "文章摘要",
    "keywords": "关键词1,关键词2",
    "author_id": 1,
    "original_filename": "article.html",
    "view_count": 100,
    "created_at": "2025-03-07T10:00:00Z",
    "updated_at": "2025-03-07T10:00:00Z",
    "tags": [
      {
        "id": 1,
        "name": "技术",
        "color": "#3498db"
      }
    ],
    "html_content": "<div>文章HTML内容...</div>",
    "html_path": "articles/1/index.html",
    "processing_status": "completed",
    "original_html_url": "https://example.com/original"
  }
}
```

### 上传文件创建文章

```http
POST /api/v1/articles/upload
```

**需要认证**: ✅

**请求类型**: `multipart/form-data`

**表单参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | file | 是 | HTML 文件 |
| title | string | 是 | 文章标题 (1-255字符) |
| summary | string | 是 | 文章摘要 |
| keywords | string | 是 | 文章关键词 |
| tag_ids | string | 否 | 标签ID列表，逗号分隔 (如: "1,2,3") |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "文章标题",
    "source_url": null,
    "summary": "文章摘要",
    "keywords": "关键词1,关键词2",
    "author_id": 1,
    "original_filename": "upload.html",
    "view_count": 0,
    "created_at": "2025-03-07T10:00:00Z",
    "updated_at": "2025-03-07T10:00:00Z",
    "tags": [],
    "html_content": null,
    "html_path": null,
    "processing_status": "completed",
    "original_html_url": null
  }
}
```

**错误响应**

- `413`: 文件过大
- `400`: 标题/摘要/关键词为空

### 从 URL 导入文章

```http
POST /api/v1/articles/from-url-html
```

**需要认证**: ✅

**请求体**

```json
{
  "url": "https://example.com/article",
  "tag_ids": [1, 2, 3],
  "title": "自定义标题（可选）"
}
```

**字段说明**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | 是 | 文章 URL (1-1000字符) |
| tag_ids | array | 否 | 标签ID列表 |
| title | string | 否 | 自定义标题，不提供则由AI提取 |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "AI提取的标题",
    "source_url": null,
    "summary": "AI提取的摘要",
    "keywords": "AI提取的关键词",
    "author_id": 1,
    "original_filename": null,
    "view_count": 0,
    "created_at": "2025-03-07T10:00:00Z",
    "updated_at": "2025-03-07T10:00:00Z",
    "tags": [
      {
        "id": 1,
        "name": "技术",
        "color": "#3498db"
      }
    ],
    "html_content": "<div>处理后的HTML内容...</div>",
    "html_path": "articles/1/index.html",
    "processing_status": "completed",
    "original_html_url": "https://example.com/article"
  }
}
```

**错误响应**

- `400`: AI提取失败、URL无效
- `409`: 文章已导入

### 更新文章

```http
PUT /api/v1/articles/{article_id}
```

**需要认证**: ✅ (仅作者和管理员)

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| article_id | integer | 文章ID |

**请求体**

```json
{
  "title": "string (可选, 1-255字符)",
  "source_url": "string (可选)",
  "summary": "string (可选)",
  "keywords": "string (可选)",
  "tag_ids": [1, 2, 3]
}
```

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "更新后的标题",
    "source_url": "https://example.com",
    "summary": "更新后的摘要",
    "keywords": "更新后的关键词",
    "author_id": 1,
    "original_filename": "article.html",
    "view_count": 100,
    "created_at": "2025-03-07T10:00:00Z",
    "updated_at": "2025-03-07T11:00:00Z",
    "tags": [
      {
        "id": 1,
        "name": "技术",
        "color": "#3498db"
      }
    ],
    "html_content": null,
    "html_path": "articles/1/index.html",
    "processing_status": "completed",
    "original_html_url": "https://example.com/original"
  }
}
```

**错误响应**

- `400`: 无权编辑此文章
- `404`: 文章不存在

### 删除文章

```http
DELETE /api/v1/articles/{article_id}
```

**需要认证**: ✅ (仅作者和管理员)

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| article_id | integer | 文章ID |

**响应**: `204 No Content`

**错误响应**

- `403`: 无权删除此文章
- `404`: 文章不存在

### 获取文章 HTML 内容

```http
GET /api/v1/articles/{article_id}/html
```

**需要认证**: ✅

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| article_id | integer | 文章ID |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "文章标题",
    "source_url": "https://example.com",
    "summary": "文章摘要",
    "keywords": "关键词1,关键词2",
    "author_id": 1,
    "original_filename": "article.html",
    "view_count": 100,
    "created_at": "2025-03-07T10:00:00Z",
    "updated_at": "2025-03-07T10:00:00Z",
    "tags": [
      {
        "id": 1,
        "name": "技术",
        "color": "#3498db"
      }
    ],
    "html_content": "<div>完整的HTML内容...</div>",
    "html_path": "articles/1/index.html",
    "processing_status": "completed",
    "original_html_url": "https://example.com/original"
  }
}
```

---

## 标签模块

### 获取所有标签

```http
GET /api/v1/tags/
```

**需要认证**: ❌

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "name": "技术",
      "color": "#3498db",
      "created_at": "2025-03-07T10:00:00Z"
    },
    {
      "id": 2,
      "name": "生活",
      "color": "#e74c3c",
      "created_at": "2025-03-07T10:00:00Z"
    }
  ]
}
```

### 获取标签详情

```http
GET /api/v1/tags/{tag_id}
```

**需要认证**: ❌

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| tag_id | integer | 标签ID |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "技术",
    "color": "#3498db",
    "created_at": "2025-03-07T10:00:00Z"
  }
}
```

### 创建标签

```http
POST /api/v1/tags/
```

**需要认证**: ✅

**请求体**

```json
{
  "name": "string (1-50字符)",
  "color": "string (可选, 十六进制颜色, 如: #3498db)"
}
```

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "技术",
    "color": "#3498db",
    "created_at": "2025-03-07T10:00:00Z"
  }
}
```

### 更新标签

```http
PUT /api/v1/tags/{tag_id}
```

**需要认证**: ✅

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| tag_id | integer | 标签ID |

**请求体**

```json
{
  "name": "string (可选, 1-50字符)",
  "color": "string (可选, 十六进制颜色)"
}
```

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "更新后的标签名",
    "color": "#e74c3c",
    "created_at": "2025-03-07T10:00:00Z"
  }
}
```

### 删除标签

```http
DELETE /api/v1/tags/{tag_id}
```

**需要认证**: ✅

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| tag_id | integer | 标签ID |

**响应**: `204 No Content`

### 获取标签下的文章

```http
GET /api/v1/tags/{tag_id}/articles?page=1&size=20
```

**需要认证**: ❌

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| tag_id | integer | 标签ID |

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认 1 |
| size | integer | 否 | 每页数量，默认 20 |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 50,
    "page": 1,
    "size": 20,
    "items": [
      {
        "id": 1,
        "title": "文章标题",
        "source_url": "https://example.com",
        "summary": "文章摘要",
        "keywords": "关键词1,关键词2",
        "author_id": 1,
        "original_filename": "article.html",
        "view_count": 100,
        "created_at": "2025-03-07T10:00:00Z",
        "updated_at": "2025-03-07T10:00:00Z",
        "tags": [
          {
            "id": 1,
            "name": "技术",
            "color": "#3498db"
          }
        ]
      }
    ]
  }
}
```

---

## 搜索模块

### 搜索文章

```http
GET /api/v1/search/articles?q=关键词&tags=1,2&page=1&size=20
```

**需要认证**: ✅

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| q | string | 否 | 搜索关键词（匹配标题、摘要、关键词） |
| tags | string | 否 | 标签ID列表，逗号分隔 (如: "1,2,3") |
| page | integer | 否 | 页码，默认 1 |
| size | integer | 否 | 每页数量，默认 20，最大 100 |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 25,
    "page": 1,
    "size": 20,
    "items": [
      {
        "id": 1,
        "title": "包含关键词的文章",
        "source_url": "https://example.com",
        "summary": "包含关键词的摘要",
        "keywords": "关键词,搜索",
        "author_id": 1,
        "original_filename": "article.html",
        "view_count": 100,
        "created_at": "2025-03-07T10:00:00Z",
        "updated_at": "2025-03-07T10:00:00Z",
        "tags": [
          {
            "id": 1,
            "name": "技术",
            "color": "#3498db"
          }
        ]
      }
    ]
  }
}
```

**搜索说明**
- 关键词搜索匹配字段：标题、摘要、关键词
- 标签筛选：可单独使用或与关键词组合
- 支持模糊匹配（icontains）

---

## 阅读记录模块

### 开始阅读文章

```http
POST /api/v1/reading/articles/{article_id}/start
```

**需要认证**: ✅

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| article_id | integer | 文章ID |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "article_id": 1,
    "article_title": "文章标题",
    "started_at": "2025-03-07T10:00:00Z",
    "ended_at": null,
    "reading_duration": 0,
    "reading_progress": 0
  }
}
```

### 结束阅读文章

```http
POST /api/v1/reading/articles/{article_id}/end
```

**需要认证**: ✅

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| article_id | integer | 文章ID |

**请求体**

```json
{
  "reading_progress": 50
}
```

**字段说明**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| reading_progress | integer | 否 | 阅读进度 (0-100)，默认 0 |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "article_id": 1,
    "article_title": "文章标题",
    "started_at": "2025-03-07T10:00:00Z",
    "ended_at": "2025-03-07T10:30:00Z",
    "reading_duration": 1800,
    "reading_progress": 50
  }
}
```

### 获取阅读历史

```http
GET /api/v1/reading/history?page=1&size=20
```

**需要认证**: ✅

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认 1 |
| size | integer | 否 | 每页数量，默认 20 |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 50,
    "page": 1,
    "size": 20,
    "items": [
      {
        "id": 1,
        "article_id": 1,
        "article_title": "文章标题",
        "started_at": "2025-03-07T10:00:00Z",
        "ended_at": "2025-03-07T10:30:00Z",
        "reading_duration": 1800,
        "reading_progress": 50
      }
    ]
  }
}
```

### 获取个人阅读统计

```http
GET /api/v1/reading/stats?page=1&size=20
```

**需要认证**: ✅

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认 1 |
| size | integer | 否 | 每页数量，默认 20 |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 10,
    "page": 1,
    "size": 20,
    "items": [
      {
        "article_id": 1,
        "article_title": "文章标题",
        "total_views": 5,
        "total_duration": 9000,
        "last_read_at": "2025-03-07T10:30:00Z"
      }
    ]
  }
}
```

### 获取文章阅读统计（管理员）

```http
GET /api/v1/reading/articles/{article_id}/stats?page=1&size=20
```

**需要认证**: ✅ (管理员权限)

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| article_id | integer | 文章ID |

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认 1 |
| size | integer | 否 | 每页数量，默认 20 |

**响应示例**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 50,
    "page": 1,
    "size": 20,
    "items": [
      {
        "article_id": 1,
        "article_title": "文章标题",
        "total_views": 100,
        "total_duration": 180000,
        "last_read_at": "2025-03-07T10:30:00Z"
      }
    ]
  }
}
```

---

## 数据模型

### UserResponse

```typescript
interface UserResponse {
  id: number;
  username: string;        // 3-50字符
  email: string;           // 邮箱格式
  role: 'admin' | 'user';  // 用户角色
  is_active: boolean;      // 是否激活
  created_at: string;      // ISO 8601格式时间戳
}
```

### ArticleResponse

```typescript
interface ArticleResponse {
  id: number;
  title: string;              // 1-255字符
  source_url: string | null;  // 来源URL
  summary: string | null;     // 文章摘要
  keywords: string | null;    // 关键词，逗号分隔
  author_id: number;          // 作者ID
  original_filename: string | null;  // 原始文件名
  view_count: number;         // 浏览次数
  created_at: string;         // ISO 8601格式时间戳
  updated_at: string;         // ISO 8601格式时间戳
  tags: TagInfo[];            // 标签列表
  html_content: string | null; // HTML内容（仅详情返回）
  html_path: string | null;   // HTML文件路径
  processing_status: string | null; // 处理状态: pending/processing/completed/failed
  original_html_url: string | null; // 原始URL（URL导入时）
}
```

### TagInfo

```typescript
interface TagInfo {
  id: number;
  name: string;   // 1-50字符
  color: string;  // 十六进制颜色，如 #3498db
}
```

### TagResponse

```typescript
interface TagResponse {
  id: number;
  name: string;   // 1-50字符
  color: string;  // 十六进制颜色，如 #3498db
  created_at: string;  // ISO 8601格式时间戳
}
```

### ReadingHistoryResponse

```typescript
interface ReadingHistoryResponse {
  id: number;
  article_id: number;
  article_title: string;
  started_at: string;       // ISO 8601格式时间戳
  ended_at: string | null;  // ISO 8601格式时间戳
  reading_duration: number; // 阅读时长（秒）
  reading_progress: number; // 阅读进度 (0-100)
}
```

### ReadingStatsResponse

```typescript
interface ReadingStatsResponse {
  article_id: number;
  article_title: string;
  total_views: number;       // 总浏览次数
  total_duration: number;    // 总阅读时长（秒）
  last_read_at: string | null; // 最后阅读时间，ISO 8601格式
}
```

---

## 附录

### 错误码说明

| HTTP状态码 | 说明 |
|-----------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 204 | 成功（无返回内容） |
| 400 | 请求参数错误或业务逻辑错误 |
| 401 | 未认证或Token无效 |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 409 | 资源冲突（如重复创建） |
| 413 | 文件过大 |
| 422 | 参数验证失败 |
| 500 | 服务器内部错误 |

### 常见错误示例

**未认证**
```json
{
  "detail": "Could not validate credentials"
}
```

**无权限**
```json
{
  "detail": "无权编辑此文章"
}
```

**资源不存在**
```json
{
  "detail": "文章不存在"
}
```

**参数验证失败**
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

### 文件上传限制

- 最大文件大小: 由服务端配置决定
- 支持的文件格式: HTML 文件

### AI 提取说明

从 URL 导入文章时，系统会：
1. 自动抓取网页内容
2. 使用 AI 提取标题、摘要、关键词
3. 处理图片（下载并转为本地链接）
4. 保存处理后的 HTML 文件
5. 失败时不会保存文章记录

### 分页说明

所有分页接口：
- `page`: 页码，从 1 开始
- `size`: 每页数量，默认 20
- `total`: 总记录数
- `items`: 当前页数据列表

---

**文档结束**

如有疑问，请联系后端开发团队。
