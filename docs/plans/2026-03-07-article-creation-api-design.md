# 文章创建接口改造设计

**日期：** 2026-03-07
**作者：** Claude
**状态：** 已批准

## 概述

改造文章创建接口，支持两种创建方式：本地上传和 URL 导入，每种方式有不同的数据要求和存储策略。

## 需求

### 方式一：本地上传文件

- 用户上传文件（HTML、MD、TXT 等）
- **title, summary, keywords 为必填项**
- 文件直接存储，不转换
- `html_path = null`
- `original_html_url = null`

### 方式二：从 URL 导入

- 下载 URL 的 HTML 内容
- **同步调用 AI 提取** title, summary, keywords
- AI 提取失败则返回错误，不保存文章
- 保存清洗后的 HTML 到 `index.html`
- `html_path = articles/{id}/index.html`
- `original_html_url = 源 URL`

## API 接口设计

### 1. 本地上传接口

**端点：** `POST /articles/upload`

**请求方式：** `multipart/form-data`

**请求参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 上传的文件 |
| title | string | **是** | 文章标题 |
| summary | string | **是** | 文章摘要 |
| keywords | string | **是** | 关键词（逗号分隔） |
| tag_ids | string | 否 | 标签ID列表 |

**响应：** `SuccessResponse[ArticleResponse]`

### 2. URL 导入接口

**端点：** `POST /articles/from-url-html`

**请求方式：** `application/json`

**请求体：**
```json
{
  "url": "string",
  "tag_ids": [int],
  "title": "string"
}
```

**响应：** `SuccessResponse[ArticleResponse]`

## 数据库字段使用

| 字段 | 本地上传 | URL 导入 |
|------|----------|----------|
| html_path | `null` | `articles/{id}/index.html` |
| original_filename | 原始文件名 | `null` |
| original_html_url | `null` | 源 URL |
| summary | 用户填写 | AI 提取 |
| keywords | 用户填写 | AI 提取 |
| processing_status | - | `"completed"` |

## 文件存储结构

```
uploads/
└── articles/
    └── {article_id}/
        ├── {original_filename}    # 本地上传
        └── index.html              # URL 导入
```

## 文件读取逻辑

```python
async def get_article_file_path(article: Article) -> str:
    """获取文章文件的绝对路径"""
    if article.html_path:
        # URL 导入：使用 html_path
        return os.path.join(settings.upload_dir, article.html_path)
    elif article.original_filename:
        # 本地上传：使用 id + original_filename
        return os.path.join(
            settings.upload_dir,
            "articles",
            str(article.id),
            article.original_filename
        )
    else:
        raise FileNotFoundError("文章文件不存在")
```

## 错误处理

| 场景 | HTTP 状态 | 错误消息 |
|------|-----------|----------|
| 本地上传缺少必填项 | 400 | "标题、摘要和关键词为必填项" |
| URL 格式无效 | 400 | "URL 格式无效" |
| URL 已导入 | 409 | "该文章已导入" |
| URL 下载失败 | 400 | "无法访问网页" |
| AI 提取失败 | 500 | "AI 提取失败，请稍后重试" |

## 实现文件清单

1. `backend/api/v1/endpoints/articles/router.py` - 更新接口验证
2. `backend/controllers/article_controller.py` - 更新业务逻辑
3. `backend/utils/article_storage.py` - 添加文件定位函数
4. `backend/schemas/article.py` - 更新 Schema 验证

## 测试计划

1. 本地上传接口测试
   - 必填字段验证
   - 文件存储验证
   - 数据库字段验证
2. URL 导入接口测试
   - URL 下载测试
   - AI 提取测试
   - 错误处理测试
3. 文件读取测试
   - 两种来源的文件都能正确读取
