---
tags:
  - openclaw
  - claude-code
created: 2026-05-09 07:36:00
updated: 2026-05-09 07:36
---

# Windows + WSL + Ubuntu 环境下的 Claude Code 部署与配置

> [!info] 版本说明
> 本文档基于 **@anthropic-ai/claude-code 2.1.109** 编写，适用于 Windows 11 + WSL2 (Ubuntu 22.04) 环境。
> 安装前请确认最新版本：`claude --version`

## 简要概述

> [!info] Claude Code 是什么
> Claude Code 是 Anthropic 官方发布的终端编程智能体（coding agent），支持交互式会话和非交互式管道模式。
> 核心优势：直接操作文件系统、执行 shell 命令、集成 Git 工作流，是当前最强的 AI 编程助手之一。
>
> Claude Code 支持两种认证方式：
> 1. **官方 Anthropic API**（`api.anthropic.com`）：需要 Anthropic API Key
> 2. **自定义 API 代理**：兼容 Anthropic API 协议的第三方服务，通过 `ANTHROPIC_BASE_URL` 路由
>
> 本文档基于第二种方式（自定义 API 代理），通过小米 Token Plan 服务使用 `mimo-v2-pro` 模型。

**架构概览**

```
Windows 11 宿主机
  └── WSL2 (Ubuntu 22.04)
        ├── Node.js v22.x
        ├── OpenClaw Gateway (127.0.0.1:18789)
        ├── Claude Code (@anthropic-ai/claude-code 2.1.109)
        │     └── 连接: token-plan-cn.xiaomimimo.com/anthropic (自定义代理)
        └── OpenSpace MCP (systemd user service, SSE on :8081)
```

## 前置条件

> [!caution] 必需项
> - **Node.js ≥ 22**（参考主文档 [../Openclaw本地部署笔记/Windows+WSL+Ubuntu本地部署.md](../Openclaw本地部署笔记/Windows+WSL+Ubuntu本地部署.md) step1）
> - **Anthropic API Key** 或**自定义 API 代理的 Token**
>   - 官方 API 注册：[console.anthropic.com](https://console.anthropic.com)
>   - 自定义代理：本文使用 `token-plan-cn.xiaomimimo.com`，需获取对应 Token

## 安装 Claude Code

### step1: 安装

```bash
# 全局安装（推荐）
npm install -g @anthropic-ai/claude-code

# 验证安装
claude --version
# 预期输出: 2.1.109 (Claude Code)
```

> [!tip] 如果 openclaw 已安装
> Claude Code 通常随 OpenClaw 一起安装，无需重复执行。可通过 `which claude` 确认是否已存在。

### step2: 配置 API（自定义代理模式）

Claude Code 通过 `~/.claude/settings.json` 配置 API 连接信息：

```bash
mkdir -p ~/.claude
```

创建/修改 `~/.claude/settings.json`：

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://token-plan-cn.xiaomimimo.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "tp-your-token-here",
    "ANTHROPIC_MODEL": "mimo-v2-pro",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "mimo-v2-pro",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "mimo-v2-pro",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "mimo-v2-pro"
  }
}
```

> [!tip] 字段说明
>
> | 字段 | 说明 |
> |------|------|
> | `ANTHROPIC_BASE_URL` | API 代理地址，替换为你使用的服务 |
> | `ANTHROPIC_AUTH_TOKEN` | 代理服务的认证 Token |
> | `ANTHROPIC_MODEL` | 默认使用的模型 |
> | `ANTHROPIC_DEFAULT_SONNET_MODEL` | Sonnet 级别任务使用的模型 |
> | `ANTHROPIC_DEFAULT_OPUS_MODEL` | Opus 级别任务使用的模型 |
> | `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Haiku 级别任务使用的模型 |

#### 方式 B：使用官方 Anthropic API

如果使用 Anthropic 官方 API（不需要代理），配置如下：

```json
{
  "env": {
    "ANTHROPIC_API_KEY": "sk-ant-your-key-here"
  }
}
```

> [!caution] 安全提醒
> - `settings.json` 包含认证信息，确保文件权限：`chmod 600 ~/.claude/settings.json`
> - 不要将此文件提交到 Git 仓库
> - `ANTHROPIC_AUTH_TOKEN` 和 `ANTHROPIC_API_KEY` 二选一，不要同时配置

### step3: 验证安装与连接

```bash
# 1. 检查版本
claude --version

# 2. 非交互式测试（推荐）
claude -p "say hello in one word" 2>&1 | head -5

# 预期成功输出类似：
# Hello!

# 3. 如果看到以下错误，说明 Token 无效：
# Error: 401 Unauthorized
# 解决：检查 settings.json 中的 ANTHROPIC_AUTH_TOKEN 是否正确
```

## 使用方法

### 交互式模式

```bash
# 直接启动交互式会话
claude

# 指定工作目录
claude --add-dir /path/to/project

# 继续上次会话
claude -c
```

### 非交互式模式（管道模式）

```bash
# 单次任务
claude -p "explain what this project does"

# 从 stdin 读取内容
echo "refactor this function" | claude -p -

# 带最大预算控制
claude -p "optimize this code" --max-budget-usd 0.5
```

### 常用交互命令

启动交互式会话后，可使用以下斜杠命令：

| 命令 | 说明 |
|------|------|
| `/help` | 显示帮助 |
| `/clear` | 清除上下文 |
| `/compact` | 压缩上下文以节省 token |
| `/cost` | 查看当前会话消耗 |
| `/model` | 切换模型 |
| `/permissions` | 管理工具权限 |
| `/mcp` | 管理 MCP 服务器 |
| `/config` | 查看/修改配置 |

### 与 OpenClaw 集成（ACP 模式）

Claude Code 可作为 OpenClaw 的 ACP（Agent Coding Partner）子代理使用：

```bash
# 在 OpenClaw 中 spawn 一个 Claude Code 会话
# 通过 sessions_spawn 使用 runtime="acp"
```

> [!info] ACP 集成
> OpenClaw 支持通过 `sessions_spawn(runtime="acp", agentId="claude-code")` 调用 Claude Code。
> 配置方式参考主文档 [../Openclaw本地部署笔记/Windows+WSL+Ubuntu本地部署.md](../Openclaw本地部署笔记/Windows+WSL+Ubuntu本地部署.md) 的 ACP 配置章节。

## 模型切换

### 交互式切换

在会话中输入 `/model` 可交互式切换模型：

```
/model mimo-v2-omni
```

### 通过配置切换

修改 `~/.claude/settings.json` 中的模型字段：

```json
{
  "env": {
    "ANTHROPIC_MODEL": "mimo-v2-omni",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "mimo-v2-omni",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "mimo-v2-pro",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "mimo-v2-flash"
  }
}
```

> [!tip] 模型分级使用建议
> - **Haiku**（`mimo-v2-flash`）：快速、低成本，适合简单查询
> - **Sonnet**（`mimo-v2-pro`）：均衡性能，适合日常编程
> - **Opus**（`mimo-v2-pro`）：最强推理，适合复杂架构决策

## 安全与权限

### 权限模式

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| 默认 | 每次工具调用需确认 | 生产环境，安全第一 |
| `--dangerously-skip-permissions` | 跳过所有权限检查 | 沙箱/离线环境 |
| `--allow-dangerously-skip-permissions` | 允许但不默认启用 | 按需使用 |

### 工具白名单

```bash
# 只允许 git 和 Edit 工具
claude --allowedTools "Bash(git *)" Edit

# 禁止特定工具
claude --disallowedTools "Bash(rm *)"
```

## 常见问题排查

### Q1: 401 Unauthorized

```text
Error: 401 Unauthorized
```

**原因**：API Token 无效或未配置。

**解决**：
1. 确认 `~/.claude/settings.json` 存在且格式正确
2. 检查 `ANTHROPIC_AUTH_TOKEN` 是否为有效 Token
3. 如使用官方 API，检查 `ANTHROPIC_API_KEY` 是否正确

### Q2: 连接超时

```text
Error: connect ETIMEDOUT
```

**原因**：无法连接到 `ANTHROPIC_BASE_URL` 指定的地址。

**解决**：
1. 检查网络连通性：`curl -s https://token-plan-cn.xiaomimimo.com/anthropic/v1/models`
2. 如在中国大陆，可能需要代理或使用国内 API 代理服务
3. 检查 WSL 的 DNS 配置：`cat /etc/resolv.conf`

### Q3: settings.json 格式错误

```text
Error: Unexpected token in JSON
```

**原因**：JSON 格式有误（常见于多余逗号）。

**解决**：
```bash
# 验证 JSON 格式
python3 -m json.tool ~/.claude/settings.json
```

### Q4: 配置文件位置

| 文件 | 路径 | 用途 |
|------|------|------|
| settings.json | `~/.claude/settings.json` | API 配置 + 环境变量 |
| 会话数据 | `~/.claude/sessions/` | 历史会话 |
| 历史记录 | `~/.claude/history.jsonl` | 命令历史 |
| 项目配置 | `~/.claude/projects/` | 按项目存储的配置 |
| 插件 | `~/.claude/plugins/` | 已安装的插件 |

## 运维命令

```bash
# 查看版本
claude --version

# 更新（如果有新版本）
npm update -g @anthropic-ai/claude-code

# 查看配置
cat ~/.claude/settings.json

# 清除会话历史
rm ~/.claude/sessions/*

# 调试模式（排查连接问题）
claude -d "test connection"

# 作为 MCP Server 运行
claude mcp
```

---

## 变更记录

| 版本 | 日期 | 主要改动 |
|------|------|---------|
| 1.0 | 2026-05-09 | 初始版本，基于 @anthropic-ai/claude-code 2.1.109 |
