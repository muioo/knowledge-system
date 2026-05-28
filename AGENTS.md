# 项目说明

## 项目目标

本项目是一个基于 FastAPI + React 的知识管理系统，支持用户认证、标签管理、文章上传、URL 导入、HTML 内容存储、阅读记录和阅读统计。

文章 URL 导入可选择使用智谱大模型提取标题、正文、摘要和关键词。智谱 API Key 由前端在导入时临时提供，后端不保存、不从配置文件读取大模型 API Key。默认模型为 `glm-4-flash`，前端支持固定模型下拉和自定义模型名称。

爬虫模块优先使用通用 HTML 抓取和清洗；遇到微信公众号、知乎等特殊站点时，在 `backend/utils/html_fetcher.py` 中增加站点级适配。知乎可通过环境变量 `ZHIHU_COOKIE` 提供登录 Cookie。

## 目录结构

- `backend/`：FastAPI 后端。
- `backend/api/v1/endpoints/`：API 路由层，只负责请求解析、鉴权和响应封装。
- `backend/controllers/`：业务编排层。
- `backend/models/`：TortoiseORM 数据模型。
- `backend/schemas/`：Pydantic 请求和响应模型。
- `backend/utils/`：HTML 抓取、图片处理、文章存储、AI 提取等工具。
- `backend/tests/`：后端 pytest 测试。
- `frontend/`：React + Vite 前端。
- `frontend/src/api/`：前端 API 请求封装。
- `frontend/src/pages/`：页面组件。
- `docs/`：项目文档和外部 API 参考。

## 代码风格

- 新代码优先简洁实现，不添加未被要求的抽象、配置或兼容逻辑。
- 修改代码只触碰完成需求必须触碰的文件和行。
- Python 函数必须写中文注释或 docstring，错误必须记录日志，不允许静默吞异常。
- 前后端字段命名沿用现有风格：后端请求字段使用 snake_case，前端内部状态可用 camelCase，提交 API 时转换为后端字段。
- 配置、URL、端口、密钥不得硬编码；用户级密钥只能由前端临时传入或通过环境变量运行示例脚本。
- 单文件不超过 200 行；超过时必须拆分。

## 数据库迁移

本项目使用 Aerich 管理 TortoiseORM 迁移：

```bash
aerich migrate --name "描述"
aerich upgrade
```

模型文件位于：

- `backend/models/user.py`
- `backend/models/article.py`
- `backend/models/tag.py`
- `backend/models/reading.py`

## 验证要求

- 后端行为变更优先补 pytest 测试。
- 前端变更至少运行 `npm run build`。
- 修改 AI 提取链路时，需要覆盖：未传 API Key、默认模型、自定义模型透传、AI 失败时明确报错。
