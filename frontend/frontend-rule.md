# 前端设计规则（React + TypeScript）

本项目前端基于 React + Vite，**全面使用 TypeScript，严禁 JS/TS 混用**。

## TypeScript 强制规则

- `src/` 与 `tests/` 目录内只允许 `.ts` / `.tsx` 文件，禁止出现 `.js` / `.jsx` / `.mjs` 源码。
- 纯逻辑、无 JSX 的模块统一用 `.ts`，必须显式标注函数入参与返回类型。
- 含渲染逻辑的组件统一用 `.tsx`。
- 类型定义（接口 / 类型别名）统一收敛到 `src/types/api.ts` 或就近的工具模块中导出，避免重复定义。
- 构建/工具链配置文件（`vite.config.ts`、`eslint.config.js`、`postcss.config.js`）以 `.js` 或 `.ts` 均可，但不属于源码，不得出现在 `src/`、`tests/` 中；已移除多余的 `vite.config.js` 与 `tailwind.config.js`（Tailwind v4 走 CSS-first）。
- API 地址统一使用相对路径 `/api/v1`，开发环境由 vite 代理转发、生产环境由 nginx 反向代理，不使用 `.env` 环境变量文件。
- 提交前必须通过 `npm run build` 与 `npm test`。

## 代码风格与结构

- 编写简洁、可维护且类型准确的 TypeScript 代码。
- 使用函数式和声明式编程模式；避免使用类。
- 如果文件已存在，则在已存在的文件上修改代码。

## 目录结构

```bash
frontend/
  - src/
    - api/         # API 请求封装，如 article.ts、tag.ts
    - components/  # 公共可复用 UI 组件
    - pages/       # 路由对应页面组件
    - router/      # 路由规则
    - store/       # 全局状态
    - contexts/    # React Context
    - utils/       # 无业务状态的工具函数
    - types/       # 接口请求/响应等类型声明
  - tests/         # vitest 测试（.ts）
```

## 命名约定

- 目录使用小写字母和短横线。
- 倾向于命名导出函数。
- 优先选用接口（interface）而非类型别名，因其可扩展性和合并能力。
- 避免使用枚举；改用字面量联合类型。

## 语法与格式化

- 纯函数使用 `function` 关键字。
- 组件使用函数式组件并搭配 TypeScript 接口定义 props。
- API 调用必须包含错误处理。
- 提交前必须通过全部测试。

## UI 与样式

- 样式采用 Tailwind CSS。
