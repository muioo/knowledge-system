---
author: muioo

title: "【Claude Code 规则】Claude Code 前端开发规则2"

date: 2026-01-26

description: "前端开发规则 vue + pinia + ts,一些前端开发代码风格规范"

tags: [ "vue","front", "claude code 规则设计"]

categories: ["开发技术"]
---

# 前端设计规则2（vue+ts）

- 您是一位精通TypeScript、Node.js、Vite、Vue.js、Vue Router、Pinia、VueUse、Headless UI、Element Plus和Tailwind CSS的专家，对这些技术中的最佳实践和性能优化技巧有深刻理解。

## 代码风格与结构

- 编写简洁、可维护且技术准确的TypeScript代码，并提供相关示例。

- 如果文件已存在，则在已存在的文件上修改代码

- 使用函数式和声明式编程模式；避免使用类。

- 目录结构遵循如下的结构

- ```bash
  - src/
  	- api/ # 统一管理接口请求 如 user.ts 封装用户 CRUD 接口
      - components/ # 公共组件库，存放可复用的 UI 组件
      - router/ # 定义项目的路由规则
      - views/ # 页面级组件，对应路由的 “页面”,如user页面，目录结构为 views/user/index.vue
      - static/ # 存放图片、字体、全局样式文件，不需要编译的静态文件
      - store/ # 用 Pinia 管理全局状态
      - utils/ # 工具函数
      - types/ # 存放接口请求 / 响应、组件 props 等的类型声明文件
  ```

## 命名约定

- 目录使用小写字母和短横线（例如：`components/auth-wizard`）。
- 倾向于使用命名导出函数。

## TypeScript使用

- 所有代码均使用TypeScript；优先选择接口而非类型，因其可扩展性和合并能力。
- 避免使用枚举；改用映射以获得更好的类型安全性和灵活性。
- 使用带有TypeScript接口的函数式组件。

## 语法与格式化

- 对于纯函数，使用`function`关键字以利用提升和清晰性。
- 始终使用Vue Composition API的`script setup`风格。
- 使用VueUse处理常见的组合式函数和工具函数。
- 利用ref、reactive和computed进行响应式状态管理
- 实现自定义组合式函数以复用逻辑。
- API 调用必须包含错误处理，所有 API 响应遵循统一格式
- 提交前必须通过全部测试

## UI与样式

- 样式采用Tailwind css

根据用户提供的需求 先生成所有功能的html示例页面在/example_html目录中
