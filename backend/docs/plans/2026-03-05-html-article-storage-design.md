# HTML 文章存储与 AI 提取功能设计

**日期：** 2026-03-05
**作者：** Claude
**状态：** 已批准

---

## 1. 概述

### 功能描述
允许用户通过 URL 导入网络文章，系统自动下载 HTML 原文和图片到本地存储，并使用 AI 异步提取摘要和关键词。

### 核心需求
- 原文一字不动存储 HTML 格式
- 图片下载到本地并重写链接
- 使用 readability 清洗 HTML
- 异步 AI 提取摘要和关键词
- 重复 URL 检测并拒绝
- 富文本编辑器编辑内容

---

## 2. 架构设计

### 2.1 核心模块
- **HTML 下载器**：获取网页 HTML，使用 readability 清洗
- **图片处理器**：下载图片到本地，重写链接
- **AI 提取器**：异步调用火山引擎 API
- **存储管理器**：管理 HTML 文件和图片存储

### 2.2 目录结构
```
/uploads/articles/
  └── {article_id}/
      ├── index.html       # 清洗后的 HTML
      └── images/          # 下载的图片
          ├── image1.jpg
          └── image2.png
```

### 2.3 数据流向
```
用户请求 → URL 验证 → HTML 下载 → 图片处理 → 保存 → 异步 AI 提取 → 返回结果
```

---

## 3. 组件设计

### 3.1 HTML 下载器 (`utils/html_fetcher.py`)
```python
async def fetch_html(url: str) -> str
async def clean_html(html: str) -> str
async def rewrite_base_urls(html: str, base_url: str) -> str
```

### 3.2 图片处理器 (`utils/image_processor.py`)
```python
async def extract_images(html: str) -> list[str]
async def download_image(url: str, save_path: str) -> bool
async def rewrite_image_links(html: str, mapping: dict) -> str
async def mark_failed_images(html: str, failed_urls: list) -> str
```

### 3.3 AI 异步提取器 (`utils/ai_extractor.py`)
```python
async def extract_article_async(article_id: int) -> None
```

### 3.4 API 端点
```
POST /articles/from-url-html
请求体: { url: string, tag_ids?: number[] }
响应: { article_id: number, status: "pending" }
```

### 3.5 数据库字段扩展
```python
class Article(Model):
    html_path: CharField          # 本地 HTML 文件路径
    processing_status: CharField  # pending/processing/completed/failed
    original_html_url: CharField  # 原始 URL（去重检测）
```

---

## 4. 数据流

### 4.1 导入流程
1. URL 去重检测
2. HTML 下载与清洗
3. 相对路径转绝对路径
4. 提取并下载图片
5. 重写图片链接
6. 保存 HTML 文件
7. 创建数据库记录
8. 返回文章 ID
9. [后台] 异步 AI 提取

### 4.2 查看流程
1. 读取数据库记录
2. 读取本地 HTML 文件
3. 返回完整数据

---

## 5. 错误处理

| 错误场景 | 处理方式 | 用户反馈 |
|---------|---------|---------|
| URL 无法访问 | 立即返回 400 | "无法访问该网页" |
| URL 已存在 | 立即返回 409 | "该文章已导入" |
| HTML 清洗失败 | 立即返回 400 | "无法解析网页内容" |
| 图片部分失败 | 继续执行，标记失败 | 导入成功，部分图片失败 |
| 文件保存失败 | 回滚，返回 500 | "保存失败，请重试" |
| AI 提取失败 | 不影响文章，标记 failed | 文章已导入，AI 提取失败 |

### 重试策略
- 图片下载：单次失败不重试
- AI 提取：失败后重试 2 次，间隔 5 秒

---

## 6. 安全性考虑

- readability 清洗移除恶意脚本
- 直接展示 HTML（信任已清洗内容）
- 文件路径验证防止目录遍历

---

## 7. 依赖项

### 新增依赖
```
readability-lxml  # HTML 内容提取
```

### 现有依赖
```
httpx             # HTTP 请求
beautifulsoup4    # HTML 解析
volcenginesdkarkruntime  # AI 提取
```

---

## 8. 实现优先级

1. **P0 - 核心功能**
   - HTML 下载与清洗
   - 图片下载与链接重写
   - 基本存储结构

2. **P1 - 必要功能**
   - URL 去重检测
   - 异步 AI 提取
   - 错误处理

3. **P2 - 增强功能**
   - 富文本编辑器集成
   - 图片失败标记
   - 状态查询接口

---

## 9. 测试策略

- 单元测试：各组件功能测试
- 集成测试：完整导入流程测试
- 边界测试：无效 URL、大文件、网络异常
