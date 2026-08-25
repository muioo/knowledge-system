# Hierarchical Tags and Server AI Key Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复文章标签筛选，支持任意层级标签树，并将智谱 API Key 从前端请求迁移到后端环境变量。

**Architecture:** `tags.parent_id` 形成邻接表；后端一次读取标签父子关系计算后代 ID，并以 `tags__id__in` 过滤文章。标签 API 返回包含 `parent_id` 的平铺数据，前端通过纯函数构造树。AI 提取器直接读取 Pydantic Settings 的 `ZHIPU_API_KEY`。

**Tech Stack:** FastAPI、TortoiseORM、Aerich、MySQL、Pydantic Settings、React、TypeScript、Vite、pytest、Node test runner。

## Global Constraints

- 只修改需求直接涉及的文件，不清理相邻代码。
- 新增或修改函数必须有中文注释或 docstring；异常必须记录。
- 配置和密钥不得硬编码。
- 父标签筛选必须包含所有后代标签文章。
- 项目级 `AGENTS.md` 不超过 200 行。

---

### Task 1: 后端标签树与筛选

**Files:**
- Modify: `backend/models/tag.py`
- Modify: `backend/schemas/tag.py`
- Modify: `backend/controllers/tag_controller.py`
- Modify: `backend/controllers/article_controller.py`
- Modify: `backend/api/v1/endpoints/articles/router.py`
- Test: `backend/tests/test_tag_hierarchy.py`
- Test: `backend/tests/test_article_tag_filter.py`

- [ ] 编写后代集合、循环校验和父标签过滤失败测试。
- [ ] 运行目标测试并确认因缺少层级实现而失败。
- [ ] 添加 `parent_id`、层级校验、后代遍历和组合文章查询。
- [ ] 运行目标测试并确认通过。

### Task 2: 数据库迁移

**Files:**
- Create: `backend/migrations/models/<generated>_add_tag_parent.py`
- Create: `backend/sql/add_tag_parent.sql`

- [ ] 生成并审查 Aerich 迁移。
- [ ] 编写等价、可重复检查的 MySQL 手工迁移脚本说明。
- [ ] 在本地数据库执行 Aerich upgrade 并核对外键与索引。

### Task 3: 后端环境变量 AI Key

**Files:**
- Modify: `backend/settings/config.py`
- Modify: `backend/utils/ai_extractor.py`
- Modify: `backend/schemas/article.py`
- Modify: `backend/controllers/article_controller.py`
- Modify: `backend/api/v1/endpoints/articles/router.py`
- Modify: `.env.example`
- Modify: `backend/.env`
- Test: `backend/tests/test_zhipu_ai_extractor.py`
- Test: `backend/tests/test_config.py`

- [ ] 编写环境变量读取和缺失 Key 明确报错测试。
- [ ] 运行测试并确认旧的前端 Key 参数行为导致失败。
- [ ] 删除请求中的 `api_key`，由 Settings 注入 Key。
- [ ] 运行目标测试并确认通过。

### Task 4: 前端标签树和 API Key UI

**Files:**
- Modify: `frontend/src/types/api.ts`
- Modify: `frontend/src/api/tag.ts`
- Modify: `frontend/src/api/article.ts`
- Modify: `frontend/src/pages/ArticleList.tsx`
- Modify: `frontend/src/pages/TagManage.tsx`
- Modify: `frontend/src/pages/ArticleCreate.tsx`
- Modify: `frontend/src/components/article/UrlImportFields.tsx`
- Modify: `frontend/src/components/article/ZhipuAiSettings.tsx`
- Create: `frontend/src/utils/tagTree.js`
- Test: `frontend/tests/tagTree.test.mjs`

- [ ] 编写标签树构造失败测试。
- [ ] 实现任意深度树构造、顶级入口展示和创建子标签。
- [ ] 删除 API Key 状态、输入框、类型和请求字段。
- [ ] 运行前端单元测试与 TypeScript 构建。

### Task 5: 文档与完整验证

**Files:**
- Modify: `AGENTS.md`

- [ ] 更新项目目标、目录结构、配置和层级筛选验证要求。
- [ ] 运行后端完整测试、前端测试和构建。
- [ ] 启动后端并请求健康检查。
- [ ] 检查 `git diff`，确认没有覆盖无关工作区修改。
