---
tags:
  - tauri
  - react
  - typescript
  - 环境搭建
  - frontend
  - desktop-app
created: 2026-05-25
---

# CodeObservatory 前后端环境搭建说明

## 项目简介

**CodeObservatory** 是一套基于 **Tauri 2.x + React + TypeScript** 构建的桌面应用。前端使用 React 19 + TypeScript + Vite 7，后端（Rust 层）基于 Tauri 2.x 框架，最终打包为 Windows 原生桌面程序。

### 技术栈版本参考

| 组件 | 版本 |
|------|------|
| Node.js | 24.x |
| npm | 10.x（随 Node 24 附带） |
| Rust (rustc) | 1.95 |
| Cargo | 1.95 |
| Tauri CLI | 2.x |
| React | 19.x |
| TypeScript | 5.8 |
| Vite | 7.x |
| Git | 2.x |

---

## 一、必须安装的环境

以下组件按安装顺序列出。

#### 1.1 Git

**用途**：版本控制，项目管理。

- 下载地址：[https://git-scm.com/downloads/win](https://git-scm.com/downloads/win)
- 安装建议：全部默认即可，编辑器选 VS Code（如果已安装）。

#### 1.2 Node.js

**用途**：前端运行时与包管理。

- 下载地址：[https://nodejs.org](https://nodejs.org) → 选择 **LTS（24.x）**
- 安装时勾选 **「Automatically install the necessary tools」**（会自动安装 Chocolatey 和 Python 等构建依赖，对后续 native addon 编译有帮助）。
- 安装后 npm 随同安装，无需单独处理。

#### 1.3 Rust（rustup）

**用途**：Tauri 后端的 Rust 编译工具链。

- 下载地址：[https://rustup.rs](https://rustup.rs)
- 下载 `rustup-init.exe`，运行安装。
- **安装选项**：默认选 `1) Proceed with standard installation` 即可。
- 安装完成后 **务必注销并重新登录 Windows**（或重启），确保 PATH 环境变量生效。否则 VS Code 终端可能找不到 `cargo` 命令（详见 [§4 常见问题](#4-常见问题)）。

#### 1.4 Visual Studio Build Tools

**用途**：Windows 下编译 Rust 原生代码所需的 MSVC 工具链（Tauri 编译 Windows 版本的必要条件）。

- 下载地址：[https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022)
- 安装时勾选 **「使用 C++ 的桌面开发」（Desktop development with C++）** 工作负载。
- 右侧「安装详细信息」中确保以下组件被选中：
  - MSVC v143 - VS 2022 C++ x64/x86 build tools
  - Windows 11 SDK（或 Windows 10 SDK）
  - C++ CMake tools for Windows

> **注意**：Tauri 在 Windows 上默认使用 MSVC 工具链（`stable-x86_64-pc-windows-msvc`），不要安装 GNU（MinGW）版本。

---

## 二、VS Code 推荐插件

| 插件 | 用途 |
|------|------|
| **Rust Analyzer** (`rust-lang.rust-analyzer`) | Rust 语言智能提示、类型检查、跳转 |
| **Tauri** (`tauri-apps.tauri-vscode`) | Tauri 项目配置文件 `tauri.conf.json` 的 schema 校验与智能提示 |
| **Prettier** (`esbenp.prettier-vscode`) | 前端代码自动格式化（JS/TS/JSX/TSX/JSON/CSS） |
| **ESLint** (`dbaeumer.vscode-eslint`) | 前端代码质量检查 |

#### 2.1 推荐的 VS Code 设置（`settings.json`）

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[rust]": {
    "editor.defaultFormatter": "rust-lang.rust-analyzer"
  },
  "rust-analyzer.cargo.features": "all"
}
```

---

## 三、环境自查命令

完成安装（并重新登录/重启）后，在终端中运行以下命令，全部有正常输出版本号即表示环境就绪：

```bash
node --version    # 预期: v24.x.x
npm --version     # 预期: 10.x.x
rustc --version   # 预期: rustc 1.95.x
cargo --version   # 预期: cargo 1.95.x
git --version     # 预期: git version 2.x.x
```

#### 3.1 额外验证：确认 Rust 工具链为 MSVC

```bash
rustup show active-toolchain
# 预期输出: stable-x86_64-pc-windows-msvc
```

如果输出 `stable-x86_64-pc-windows-gnu`，则需要切换到 MSVC：

```bash
rustup default stable-x86_64-pc-windows-msvc
```

---

## 四、常见问题

#### Q1：VS Code 终端找不到 `cargo` / `rustc` 命令

**原因**：rustup 安装时会修改 PATH 环境变量，但已打开的终端不会自动刷新。**

**解决方法**：
1. 关闭所有 VS Code 窗口。
2. **注销 Windows 当前用户并重新登录**（或重启电脑）。
3. 重新打开 VS Code，终端即可找到 cargo。

> 不需要手动改 PATH，rustup 已经自动做了这件事，只是需要会话刷新。

#### Q2：`npm install` 报 `MSBuild` / `cl.exe` 找不到

**原因**：未安装 Visual Studio Build Tools 或安装时未勾选 C++ 组件。**

**解决方法**：打开 Visual Studio Installer → 修改 → 勾选「使用 C++ 的桌面开发」→ 安装。

#### Q3：Tauri build 报 `error: linker 'link.exe' not found`

**原因**：同上，缺少 MSVC 工具链。**

**解决方法**：参照 Q2。

#### Q4：`npm create tauri-app@latest` 提示网络错误

**原因**：npm 默认源可能被墙。**

**解决方法**（二选一）：

```bash
# 方案 A：配置 npm 淘宝镜像
npm config set registry https://registry.npmmirror.com

# 方案 B：配置 Rust 中科大镜像（如果 crates.io 也慢）
# 在 ~/.cargo/config.toml 中添加：
[source.crates-io]
replace-with = 'ustc'

[source.ustc]
registry = "https://mirrors.ustc.edu.cn/crates.io-index"
```

#### Q5：首次 `npm run tauri dev` 非常慢

**原因**：首次运行需要下载并编译所有 Rust 依赖（包括 Tauri 核心、WebView2 等），这是正常现象。后续增量编译会快很多。**

---

## 五、项目依赖安装

#### 7.1 核心依赖

```bash
npm install @tauri-apps/api @tauri-apps/plugin-dialog @tauri-apps/plugin-fs @tauri-apps/plugin-shell
```

#### 7.2 前端 UI 依赖

```bash
npm install react react-dom react-router-dom
npm install lucide-react class-variance-authority clsx tailwind-merge
npm install framer-motion
```

#### 7.3 3D 图谱依赖

```bash
npm install three @react-three/fiber @react-three/drei @react-three/postprocessing
```

#### 7.4 图数据处理

```bash
npm install cytoscape react-cytoscapejs
npm install sigma graphology graphology-layout-forceatlas2
```

#### 5.5 开发依赖

```bash
npm install -D typescript vite @vitejs/plugin-react
npm install -D tailwindcss postcss autoprefixer tailwindcss-animate
npm install -D @tauri-apps/cli
npm install -D @types/react @types/react-dom @types/node @types/cytoscape
```

#### 5.6 一键安装全部

```bash
npm install @tauri-apps/api @tauri-apps/plugin-dialog @tauri-apps/plugin-fs @tauri-apps/plugin-shell react react-dom react-router-dom lucide-react class-variance-authority clsx tailwind-merge framer-motion three @react-three/fiber @react-three/drei @react-three/postprocessing cytoscape react-cytoscapejs sigma graphology graphology-layout-forceatlas2 && npm install -D typescript vite @vitejs/plugin-react tailwindcss postcss autoprefixer tailwindcss-animate @tauri-apps/cli @types/react @types/react-dom @types/node @types/cytoscape
```

---

## 六、项目创建

#### 7.1 创建新项目

```bash
npm create tauri-app@latest
```

交互式选项建议：

```
? Project name:  codeobservatory
? Choose your frontend framework:  React
? Choose your frontend language:  TypeScript
? Choose your package manager:  npm
? Choose your UI template:  React + TypeScript (default)
```

#### 7.2 进入项目并安装依赖

```bash
cd codeobservatory
npm install
```

#### 7.3 开发运行

```bash
npm run tauri dev
```

- 首次启动会下载 WebView2 运行时（如果系统未安装）并编译 Rust 后端，预计需要 5-15 分钟（取决于网络和机器性能）。
- 后续热更新启动通常在 30 秒内。

#### 7.4 生产构建

```bash
npm run tauri build
```

构建产物位于 `src-tauri/target/release/bundle/` 目录下，包含 `.msi` 安装包和 `.exe` 便携版。

---

## 八、项目目录结构（标准模板）

```
codeobservatory/
├── src/                    # React 前端源码
│   ├── App.tsx
│   ├── App.css
│   ├── main.tsx
│   └── assets/
├── src-tauri/              # Tauri Rust 后端
│   ├── src/
│   │   └── main.rs         # Rust 入口
│   ├── Cargo.toml          # Rust 依赖配置
│   ├── tauri.conf.json     # Tauri 配置
│   └── icons/              # 应用图标
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── node_modules/
```

---

## 九、默认模板说明

### 7.1 启动后看到什么

首次运行 `npm run tauri dev`，编译完成后会弹出一个独立桌面窗口，显示默认的 **Tauri + React 欢迎页**：

- 顶部 Tauri / Vite / React 三个 logo
- 一个输入框，提示 `Enter a name...`
- 一个 Greet 按钮

### 7.2 输入框是干什么的

这是 Tauri 官方模板自带的 **前后端桥接示例**（Demo），旨在演示 React 前端如何调用 Rust 后端的核心通信模式。

**工作流程**：

```
用户输入 name → 点击 Greet
    ↓
React invoke("greet", { name })
    ↓ (Tauri IPC 进程间通信)
Rust greet(name) 函数处理
    ↓
返回 "Hello, xxx! You've been greeted from Rust!"
    ↓
React 显示结果字符串
```

**前端代码**（`src/App.tsx`）：
```tsx
import { invoke } from "@tauri-apps/api/core";

async function greet() {
  setGreetMsg(await invoke("greet", { name }));
}
```

**后端代码**（`src-tauri/src/lib.rs`）：
```rust
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}
```

### 7.3 有何意义

这个 Demo 演示了 Tauri 的核心架构能力：

| 概念 | 说明 |
|------|------|
| **IPC 通信** | 前端通过 `invoke(command, args)` 调用 Rust 函数，无需 HTTP/WebSocket，零网络开销 |
| **双向映射** | `invoke("greet")` 自动找到 `#[tauri::command] fn greet()`，名称即约定 |
| **类型安全** | TypeScript 前端 + Rust 后端，两端都是强类型 |
| **轻量** | Tauri 窗口仅 ~5MB，不使用 Chromium，用系统原生 WebView2 |

### 7.4 后续开发

这个默认模板是你开发 CodeObservatory 的起点。实际开发中：

- 删除 `greet` 示例代码
- 在 `src/` 下编写真实业务页面和组件
- 在 `src-tauri/src/lib.rs` 中注册真正的文件监听、Git 解析、图计算等后端命令
- 保持 `invoke()` 通信模式不变

---

## 十、环境搭建检查清单

在继续开发之前，逐项确认：

- [ ] `node --version` → v24.x
- [ ] `npm --version` → 10.x
- [ ] `rustc --version` → 1.95.x
- [ ] `cargo --version` → 1.95.x
- [ ] `git --version` → 2.x
- [ ] `rustup show active-toolchain` → `stable-x86_64-pc-windows-msvc`
- [ ] VS Code 已安装 Rust Analyzer、Tauri、Prettier、ESLint 插件
- [ ] Visual Studio Build Tools 已安装「使用 C++ 的桌面开发」
- [ ] `npm create tauri-app@latest` 能正常创建项目
- [ ] `npm run tauri dev` 能成功启动开发窗口

---

*文档维护：请在环境变更后同步更新本说明。*
