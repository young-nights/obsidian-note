---
tags:
  - openclaw
  - codex
created: 2026-05-09 07:25:00
updated: 2026-05-09 07:25
---

# Windows + WSL + Ubuntu 环境下的 Codex 部署与配置

> [!info] 版本说明
> 本文档基于 **codex-cli 0.125.0** 编写，适用于 OpenClaw 多 Agent 体系中接入 Codex 的场景。
> 安装前请确认最新版本：`codex --version`

## 简要概述

> [!info] Codex 是什么
> OpenAI Codex CLI 是 OpenAI 官方发布的终端编程智能体（coding agent），支持交互式 TUI 和非交互式 CLI 两种模式。
> 它使用 OpenAI 的 **Responses WebSocket 协议**与 `api.openai.com` 通信，因此**必须配置有效的 OpenAI API Key**。
> OpenRouter 等第三方聚合服务**不支持** Codex 的 WebSocket 协议，无法替代 OpenAI API。

**架构概览**

```
Windows 11 宿主机
  └── WSL2 (Ubuntu 22.04)
        ├── Node.js v22.x
        ├── OpenClaw Gateway (127.0.0.1:18789)
        ├── Codex CLI (codex-cli 0.125.0)
        │     └── 连接: wss://api.openai.com/v1/responses (需 OpenAI API Key)
        └── OpenSpace MCP (systemd user service, SSE on :8081)
```

## 前置条件

> [!caution] 必需项
> - **Node.js ≥ 22**（参考主文档 [Windows+WSL+Ubuntu本地部署.md](./Windows+WSL+Ubuntu本地部署.md) step1）
> - **OpenAI API Key**（`sk-...` 格式，必须为**真实的 OpenAI Key**，不可用 OpenRouter 代替）
> - 注册地址：[platform.openai.com](https://platform.openai.com)

## 安装 Codex CLI

### step1: 安装

```bash
# 全局安装（推荐）
npm install -g @openai/codex

# 验证安装
codex --version
# 预期输出: codex-cli 0.125.0
```

### step2: 配置 API Key

创建 `~/.codex/auth.json`：

```bash
mkdir -p ~/.codex

cat > ~/.codex/auth.json << 'EOF'
{
  "OPENAI_API_KEY": "sk-your-real-openai-api-key-here"
}
EOF
```

> [!caution] 安全提醒
> - `auth.json` 包含明文密钥，确保文件权限正确：`chmod 600 ~/.codex/auth.json`
> - 不要将此文件提交到 Git 仓库或分享给他人
> - Key 格式为 `sk-...`（来自 [platform.openai.com](https://platform.openai.com)）

### step3: 配置模型（可选）

创建 `~/.codex/config.toml`：

```toml
# 默认模型（不配置则使用 gpt-5.5）
model = "gpt-4.1"
```

> [!tip] 可用模型
> Codex 支持所有 OpenAI Responses API 兼容的模型，常见选项：
> - `gpt-5.5`（默认，最强推理）
> - `gpt-4.1`（高性价比，推荐日常使用）
> - `gpt-5-mini`（低延迟，轻量任务）

如需指定配置文件 profile：

```toml
# 可通过 -p <profile> 切换
model = "gpt-4.1"

[profiles.fast]
model = "gpt-5-mini"

[profiles.powerful]
model = "gpt-5.5"
```

使用方式：`codex -p fast exec "your task"`

### step4: 验证安装与连接

```bash
# 1. 检查版本
codex --version

# 2. 非交互式测试（推荐）
codex exec "say hello in one word" 2>&1 | tail -5

# 预期成功输出类似：
# assistant
# Hello!

# 3. 如果看到以下错误，说明 Key 无效：
# ERROR: unexpected status 401 Unauthorized
# 解决：检查 auth.json 中的 OPENAI_API_KEY 是否正确
```

## 使用方法

### 交互式模式（TUI）

```bash
# 直接启动交互式终端
codex

# 指定模型启动
codex -m gpt-4.1

# 指定工作目录
codex --workdir /path/to/project
```

### 非交互式模式（CLI）

```bash
# 执行单次任务
codex exec "explain what this project does"

# 从 stdin 读取内容
echo "refactor this function" | codex exec -

# 指定 sandbox 模式
codex exec -s workspace-write "create a hello world script"
```

### Sandbox 模式说明

> [!info] 安全沙箱
> Codex 默认使用 `read-only` sandbox，只允许读取文件。可用模式：
>
> | 模式 | 说明 | 适用场景 |
> |------|------|---------|
> | `read-only` | 只读，不写入文件或执行命令 | 查看代码、分析 |
> | `workspace-write` | 可写入当前工作目录 | 开发任务 |
> | `danger-full-access` | 完全访问（不推荐） | 信任环境 |

安装 bubblewrap 以获得最佳沙箱体验：

```bash
sudo apt install bubblewrap
```

> [!tip] 沙箱提示
> 如果未安装 bubblewrap，Codex 会使用内置版本，功能相同但会输出 warning。
> 可通过 `codex -s workspace-write exec "..."` 指定沙箱模式。

### 与 OpenClaw 集成（ACP 模式）

Codex 可作为 OpenClaw 的 ACP（Agent Coding Partner）子代理使用：

```bash
# 在 OpenClaw 中 spawn 一个 Codex 会话
# 通过 sessions_spawn 使用 runtime="acp"
```

> [!info] ACP 集成
> OpenClaw 支持通过 `sessions_spawn(runtime="acp", agentId="codex")` 调用 Codex。
> 配置方式参考主文档 [Windows+WSL+Ubuntu本地部署.md](./Windows+WSL+Ubuntu本地部署.md) 的 ACP 配置章节。

## 常见问题排查

### Q1: 401 Unauthorized

```text
ERROR: unexpected status 401 Unauthorized
url: wss://api.openai.com/v1/responses
```

**原因**：OpenAI API Key 无效或未配置。

**解决**：
1. 确认 `~/.codex/auth.json` 存在且内容正确
2. Key 格式应为 `sk-...`（来自 OpenAI，非 OpenRouter）
3. 检查 Key 是否有余额：`curl https://api.openai.com/v1/models -H "Authorization: Bearer sk-..." | head`

### Q2: OpenRouter 能否替代？

```text
ERROR: unexpected status 401 Unauthorized: No cookie auth credentials found
url: https://openrouter.ai/api/v1/responses
```

**原因**：Codex 使用 OpenAI 专有的 **Responses WebSocket 协议**，该协议在 WebSocket 握手阶段始终尝试连接 `wss://api.openai.com/v1/responses`。OpenRouter 不支持此协议。

**结论**：**必须使用真实的 OpenAI API Key**。OpenRouter、Azure OpenAI 等替代方案均不支持 Codex 的 WebSocket 流式协议。

### Q3: Bubblewrap Warning

```text
warning: Codex could not find bubblewrap on PATH.
```

**原因**：未安装 bubblewrap 沙箱工具。

**解决**：
```bash
sudo apt install bubblewrap
```

> [!tip] 可忽略
> 此 warning 不影响功能，Codex 会自动使用内置版本。安装 bubblewrap 只是让沙箱更新。

### Q4: 配置文件位置

| 文件 | 路径 | 用途 |
|------|------|------|
| auth.json | `~/.codex/auth.json` | API Key 存储 |
| config.toml | `~/.codex/config.toml` | 模型与行为配置 |
| 会话数据 | `~/.codex/sessions/` | 历史会话 |
| 日志 | `~/.codex/logs/` | 运行日志 |

## 运维命令

```bash
# 查看版本
codex --version

# 登录（交互式，引导输入 Key）
codex login

# 登出（清除凭据）
codex logout

# 查看配置
codex --help

# 作为 MCP Server 运行（供其他 Agent 调用）
codex mcp-server
```

---

## 变更记录

| 版本 | 日期 | 主要改动 |
|------|------|---------|
| 1.0 | 2026-05-09 | 初始版本，基于 codex-cli 0.125.0 |
