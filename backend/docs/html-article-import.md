# HTML 文章导入功能

## 功能说明

支持从网络 URL 导入文章，自动下载 HTML 原文和图片到本地存储。

## API 接口

### 导入 HTML 文章

```
POST /api/v1/articles/from-url-html
Content-Type: application/json
Authorization: Bearer <token>

{
  "url": "https://example.com/article",
  "tag_ids": [1, 2]
}
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "article_id": 123,
    "status": "pending",
    "message": "文章导入成功，AI 提取中"
  }
}
```

### 获取文章 HTML 内容

```
GET /api/v1/articles/{id}/html
Authorization: Bearer <token>
```

## 错误码

- 400: URL 无法访问或格式错误
- 409: URL 已导入
- 500: 服务器内部错误

## 文件存储

```
/uploads/articles/
  └── {article_id}/
      ├── index.html
      └── images/
          ├── img_0001.jpg
          └── img_0002.png
```
