# CodeObservatory（代码演化观察站）— 项目方案

## 概述
独立跨平台桌面应用。

**核心宗旨**：解决使用智能体（AI Agent）修改项目文件时的黑盒环境问题——让文件变更可追踪，利用关系图谱进行版本追踪，文件链接管理。

UI 设计借鉴 Cursor / Windsurf / Linear 现代风格：深色主题、左侧边栏导航、玻璃态材质。

## 技术栈

| 层 | 选型 |
|---|---|
| 桌面框架 | Tauri 2.x |
| 前端 | React 19 + Vite 6 + TypeScript |
| UI | Tailwind v3（布局）+ 自定义 co-* CSS 设计系统 |
| 动效 | 纯 CSS keyframes（已移除 framer-motion） |
| 图可视化 | Cytoscape.js |
| 后端 | Rust（notify / rusqlite / serde） |
| 本地数据库 | SQLite（每项目 .observatory/db.sqlite） |
| Git 仓库 | [github.com/young-nights/CodeObservatory](https://github.com/young-nights/CodeObservatory) |

## 多项目隔离设计

**原则**：每个被追踪项目的观测数据独立存储，不存在全局/集中式数据库。

```
projectA/.observatory/
├── changes/     # 变更笔记（Markdown）
├── entities/    # 业务模块笔记（预留）
├── graphs/      # 图配置（预留）
└── db.sqlite    # 索引数据库

projectB/.observatory/  # 完全独立，互不干扰
```

应用全局配置（最近打开列表等）存储在系统标准配置目录。

## 项目结构（当前）

```
code-observatory/
├── src/                       # React 前端
│   ├── components/
│   │   ├── layout/            # AppLayout, Sidebar, TopBar
│   │   ├── project/           # ProjectSelector（首页）
│   │   └── ui/                # Button, Card, Badge, Tabs, Tooltip...
│   ├── pages/                 # Dashboard, Timeline, Graph
│   ├── hooks/                 # useObservatory（项目/Watcher/变更/Graph）
│   ├── lib/                   # api.ts, types.ts, utils.ts
│   ├── styles/                # co-theme.css（暗色设计系统）
│   ├── tailwind.css           # @tailwind 指令（布局）
│   └── index.css              # 纯 CSS 主题（颜色/背景/动画）
├── src-tauri/                 # Rust 后端
│   └── src/
│       ├── commands/          # project, watcher, changes, graph
│       ├── lib.rs             # Tauri builder + 插件注册
│       ├── main.rs            # 入口
│       └── state.rs           # AppState
├── components.json            # shadcn/ui 配置
└── 配置文件（vite, tailwind, postcss, tsconfig）
```

## 核心功能

### 已实现（MVP 阶段）

| 功能 | 说明 |
|------|------|
| 项目选择器 | Android Studio 风格双栏布局，深色主题 |
| 文件监听 | notify crate，自动过滤 .git/.observatory |
| 变更记录 | Markdown 存入 .observatory/changes/ |
| SQLite 索引 | 变更元数据存入 db.sqlite |
| Dashboard | 统计卡片 + 最近变更列表 |
| Timeline | 时间线变更历史 + 变色标签 |
| Graph | Cytoscape.js 文件关系图（暗色主题） |
| 多项目隔离 | 每项目独立 .observatory/ 目录 |

### 待实现

- Canvas 拖拽画布（React Flow）
- Semantic Diff 查看器（Monaco Editor）
- AI Auditor 集成
- 搜索/过滤/导出

## 开发路线图

| 阶段 | 内容 | 状态 |
|------|------|------|
| 阶段 1 | MVP — 项目选择 + 监听 + Timeline + Graph | ✅ 完成 |
| 阶段 2 | Canvas + Semantic Diff + 业务实体 | 🔲 待开发 |
| 阶段 3 | AI Auditor + 搜索/导出 + 打包分发 | 🔲 待开发 |
| 阶段 4 | 插件系统 + 团队协作 | 🔲 规划中 |

## 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|------------|
| v0.1 | 2026-05-25 | 初始方案：Tauri + React 技术栈、MVP 功能定义 |
| v0.2 | 2026-05-26 | 新增多项目隔离设计，WSL2→Windows 路径统一 |
| v0.3 | 2026-05-26 | MVP 开发完成，8 个 Rust commands + 7 个 React 页面/组件 |
| v0.4 | 2026-05-26 | UI 全面重设计：Android Studio 风格、co-theme CSS 系统、shadcn/ui 组件 |
| v0.5 | 2026-05-26 | 添加 Dark/Light 主题切换（useTheme hook + localStorage 持久化 + CSS 变量适配） |
| v0.6 | 2026-05-26 | 宇宙星河图谱 + Preciaion Instrument 设计系统（OKLCH 色彩、Georgia serif、4pt 间距、移除全反模式） |
