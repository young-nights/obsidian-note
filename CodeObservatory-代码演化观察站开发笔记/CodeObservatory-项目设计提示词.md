# CodeObservatory 项目设计提示词

## 用途
本文档记录了 CodeObservatory 项目的完整设计上下文，用于 AI Agent 理解和执行开发任务时的参考。每次向 AI 分发任务前，将此文档作为上下文传入。

---

## 一、项目定位

CodeObservatory（代码演化观察站）是一个独立的跨平台桌面应用，专门用于追踪和可视化多 Agent 代码变更。它不是 IDE 插件，不是 Obsidian 附属，而是一个完整独立的桌面工具。

**核心使命**：让开发者能直观看到代码库中由 AI Agent 产生的每一次变更——谁改了什么，影响了哪些模块，变更频率如何。

## 二、技术架构

```
┌─────────────────────────────────────────┐
│              Tauri 2.x Shell             │
│  ┌───────────────┐  ┌─────────────────┐ │
│  │  React 19 SPA │  │  Rust Backend   │ │
│  │  (Vite 6)     │◄─┤  (notify/       │ │
│  │               │  │   rusqlite/      │ │
│  │  Layout:      │  │   serde)        │ │
│  │  Tailwind v3  │  │                 │ │
│  │  + co-* CSS   │  │  Commands:      │ │
│  │               │  │  project/watcher│ │
│  │  UI: custom   │  │  /changes/graph │ │
│  │  shadcn-like  │  │                 │ │
│  └───────────────┘  └─────────────────┘ │
└─────────────────────────────────────────┘
         │                      │
         ▼                      ▼
   WebView2 (Win)         .observatory/
   WKWebView (Mac)        └── db.sqlite
   WebKitGTK (Linux)          changes/*.md
```

## 三、设计系统

### 3.1 颜色系统
- 背景：`#09090b`（neutral-950）
- 卡片：`#121215`
- 侧栏：`#0b0b0e`
- 主色：`#4f46e5` → `#7c3aed` 渐变
- 强调：`#818cf8`（indigo-400）
- 文字主：`#fafafa`，次要：`#a1a1aa`，弱化：`#71717a`

### 3.2 材质
- 玻璃态：`rgba(11,11,14,0.85)` + `backdrop-blur(20px)`
- 卡片：`background: var(--co-bg-card) + border: 1px solid var(--co-border)`
- 悬停：`background: var(--co-bg-hover) + border-color 过渡`

### 3.3 动效策略
- 使用纯 CSS keyframes（co-fade-in, co-scale-in, co-stagger）
- 不用 framer-motion（避免跨 OS 依赖问题）
- 页面切换：300ms ease-out
- 列表交错：nth-child delays

### 3.4 布局规范
- 左侧栏 210px 固定宽，玻璃态背景
- 顶部栏 48px 高，玻璃态
- 内容区自适应剩余空间
- 间距系统：4px 基数（Tailwind 默认）

## 四、多项目隔离

**核心原则**：每个被追踪项目拥有自己独立的 `.observatory/` 数据目录。

```
工作原理：
1. 用户选择项目目录（如 /path/to/my-app）
2. CodeObservatory 检测/创建 /path/to/my-app/.observatory/
3. 所有观测数据（变更记录、图数据、SQLite）写入该目录
4. 切换到另一个项目时，加载另一个 .observatory/
5. 数据完全隔离，互不可见
```

## 五、CSS 架构（重要）

由于 WSL2 ↔ Windows 跨文件系统 Tailwind PostCSS 编译存在兼容性问题，项目采用**混合 CSS 策略**：

| 文件 | 内容 | 处理方式 |
|------|------|----------|
| `src/tailwind.css` | 仅 `@tailwind base/components/utilities` | PostCSS → 布局类 |
| `src/index.css` | 纯 CSS（632 行 co-* 类，零 @tailwind） | 直接加载，保证执行 |

**规则**：
- 布局/间距/弹性盒 → Tailwind 工具类（flex, grid, p-*, m-*, w-*, h-*）
- 颜色/背景/边框/阴影/圆角/动效 → co-* 纯 CSS 类
- 所有 co-* 类定义在 `src/index.css` 中
- 新组件引用规则：能用 co-* 的不用 Tailwind 颜色类

## 六、开发规则

### 6.1 代码规范
- 所有代码注释使用英文
- TypeScript 严格模式
- 组件文件名 PascalCase，工具文件 camelCase

### 6.2 路径约束
- 唯一开发路径：`I:\GitHub-young-nights\CodeObservatory`
- WSL2 通过 `/mnt/i/` 读写源码
- **禁止**从 WSL2 在该路径执行 npm/npx/cargo（会污染 node_modules）
- 编译/运行由用户在 Windows PowerShell 完成

### 6.3 文档联动
- 修改业务逻辑 → 同步更新本提示词文档
- 每次推送代码 → 同步推送 Obsidian 笔记仓库
- 文档仓库：`git@github.com:young-nights/obsidian-note.git`

## 七、当前状态

### 已完成
- ✅ Tauri 2 + React 19 + Vite 6 脚手架
- ✅ 项目选择器（Android Studio 风格双栏布局）
- ✅ 文件监听（notify crate）
- ✅ 变更记录 + SQLite 索引
- ✅ Dashboard（统计卡片 + 最近变更）
- ✅ Timeline（时间线列表 + 变色标签）
- ✅ Graph（Cytoscape 暗色主题）
- ✅ shadcn 风格 UI 组件库（button/card/badge/tabs/tooltip/separator/avatar/scroll-area）
- ✅ 布局组件（Sidebar/TopBar/AppLayout）
- ✅ 暗色主题 CSS 设计系统（co-* 类）
- ✅ GitHub 仓库推送

### 待实现
- 🔲 Canvas 拖拽画布
- 🔲 Monaco Editor Diff 视图
- 🔲 项目内搜索/过滤
- 🔲 AI Auditor 集成
- 🔲 打包分发（.exe/.dmg/.AppImage）

## 八、AI Agent 开发约定

向 AI 子 Agent 分发 CodeObservatory 开发任务时，请附带以下关键信息：

1. **项目路径**：`I:\GitHub-young-nights\CodeObservatory`（WSL2 中 `/mnt/i/GitHub-young-nights/CodeObservatory`）
2. **禁止执行**：npm/npx/cargo
3. **CSS 策略**：颜色/背景用 co-* 类，布局用 Tailwind
4. **代码注释**：英文
5. **任务完成后**：更新本提示词文档「七、当前状态」部分
