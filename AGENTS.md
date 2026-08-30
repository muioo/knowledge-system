# 项目说明

## 项目目标

本项目是一个基于 FastAPI + React 的知识管理系统，支持用户认证、多级标签管理、文章上传、URL 导入、HTML 内容存储、阅读记录和阅读统计。

标签使用 `parent_id` 建立任意深度层级；标签管理页以顶级标签为入口展开子树，按父标签筛选文章时必须包含父标签自身及全部后代标签。

文章 URL 导入可选择使用大模型提取标题、正文、摘要和关键词。AI 供应商支持智谱（SDK 专路）、千问/百炼（OpenAI 兼容）与自定义 OpenAI 兼容服务，密钥仅由后端环境变量提供（`ZHIPU_API_KEY` / `DASHSCOPE_API_KEY`+`DASHSCOPE_WORKSPACE_ID` / `CUSTOM_API_KEY`+`CUSTOM_BASE_URL`），前端不得采集或发送密钥。模型选择为用户级配置：登录用户在导入页选择供应商并录入模型，保存后绑定账号（`user_ai_settings` 表），未绑定时用服务端默认模型。

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
- `frontend/src/components/tag/`：层级标签树组件。
- `frontend/src/utils/tagTree.js`：将平铺标签组装为顶级入口树。
- `docs/`：项目文档和外部 API 参考。

## 代码风格

- 新代码优先简洁实现，不添加未被要求的抽象、配置或兼容逻辑。
- 修改代码只触碰完成需求必须触碰的文件和行。
- Python 函数必须写中文注释或 docstring，错误必须记录日志，不允许静默吞异常。
- 前后端字段命名沿用现有风格：后端请求字段使用 snake_case，前端内部状态可用 camelCase，提交 API 时转换为后端字段。
- 配置、URL、端口、密钥不得硬编码；智谱密钥仅从后端 `ZHIPU_API_KEY` 环境变量读取。
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

标签层级迁移位于 `backend/migrations/models/2_20260803214235_add_tag_parent.py`，将 `tags.parent_id` 设为可空的自关联外键。

## 验证要求

- 后端行为变更优先补 pytest 测试。
- 前端变更至少运行 `npm run build`。
- 修改 AI 提取链路时，需要覆盖：未配置 `ZHIPU_API_KEY`、默认模型、自定义模型透传、旧 `api_key` 字段被拒绝、AI 失败时明确报错。
- 前端文章列表的搜索、标签筛选和翻页必须组合保留查询参数；修改后至少执行构建，并手工验证标签切换、取消筛选和翻页。
- 多级标签变更需要覆盖：顶级树展示、子标签创建、循环父级拒绝、有子标签时拒绝删除，以及父标签文章筛选包含所有后代。
