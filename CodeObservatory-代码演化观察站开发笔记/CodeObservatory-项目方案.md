# CodeObservatory（代码演化观察站）— 项目方案

## 概述
独立跨平台桌面应用，完全独立于 Obsidian，但 UI/UX 高度借鉴其笔记 + Graph + Canvas 体验。专注解决多 Agent 代码变更的可视化追踪痛点。

## 技术栈

| 层 | 选型 |
|---|---|
| 桌面框架 | Tauri 2.x |
| 前端 | React + Vite + TypeScript |
| UI | Shadcn/UI + Tailwind |
| 图可视化 | Cytoscape.js（网络图）+ React Flow（Canvas 拖拽） |
| 代码编辑器 | Monaco Editor（diff 视图） |
| Markdown | React Markdown + 双向链接解析 |
| 后端 | Rust（notify / git2 / tree-sitter） |
| 本地数据库 | SQLite |
| 代码解析 | Tree-sitter（可选） |

替代方案：Electron（更快上手，体积大）、Flutter Desktop（图生态弱）、Python+PyQt

## 项目结构

```
code-observatory/
├── src/                     # React 前端
│   ├── components/          # Graph, Canvas, Timeline 等
│   ├── pages/               # Dashboard, Project, GraphView
│   └── lib/                 # 图数据处理、API 调用
├── src-tauri/               # Tauri Rust 后端
│   ├── src/
│   │   ├── commands/        # fs, git, parse
│   │   └── main.rs
│   └── tauri.conf.json
├── observatory-vault/       # 本地知识库
│   ├── changes/             # 变更笔记
│   ├── entities/            # 业务模块笔记
│   ├── graphs/              # 保存的图配置
│   └── db.sqlite
├── package.json
└── tauri.conf.json
```

## 核心功能

### 1. 变更捕获
- CLI Wrapper：`observatory-agent run "prompt"` → Agent 强制输出 JSON 报告
- Git post-commit hook + 文件监听，自动检测 AI 风格 commit
- 结构化记录：文件、diff、业务影响、自述

### 2. 知识库
- 本地 Markdown + JSON 存储，类似 Obsidian vault
- 双向链接解析

### 3. 可视化
- **Impact Graph**：业务逻辑影响图（节点：业务模块、代码文件、变更事件；边：影响强度）
- **Timeline**：时间轴变更历史
- **Canvas**：可拖拽画布，组合文件、变更、业务笔记
- **Semantic Diff**：增强 diff 视图，突出业务逻辑变化

### 4. 审计与回滚
- 一键查看影响、AI 辅助评估
- Git tag 回滚

### 5. 其他
- 搜索、过滤、高亮风险变更、导出报告

## 性能设计
- 大项目用 Web Worker 处理图计算
- 增量索引，只解析变更文件

## 开发路线图

### 阶段 1（MVP，2-4 周）
- Tauri + React 项目初始化
- 项目选择 + 文件夹监听
- 基本变更记录（手动/JSON 导入）
- Timeline 列表 + 简单 Graph（Cytoscape）

### 阶段 2
- Canvas 拖拽
- Semantic Diff 查看器
- 业务实体笔记 + 双向链接

### 阶段 3
- AI Auditor 集成（本地/远程 LLM 评估影响）
- 高级过滤、搜索、导出
- 打包分发（.dmg / .exe / .AppImage）

### 阶段 4
- 插件系统、团队协作（可选）

## 目标平台
Windows / macOS / Linux，完全本地运行
