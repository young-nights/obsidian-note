---
tags:
  - openclaw
created: 2026-04-02 18:19:00
updated: 2026-09-20 10:38
---
# <font size=4>Windows + WSL + Ubuntu + OpenClaw 本地部署

> [!info] 版本说明
> 本文档基于 **OpenClaw 2026.9.4 (3a9d69d)** + **Ubuntu 26.04** 编写，适用于 2026.9.x 系列版本。
> 环境：WSL2 (Linux 6.18.33.2-microsoft-standard) + Node.js v24.21.0
> 安装前请确认最新版本：`openclaw --version`

## <font size=3>简要概述

<font size=2>

> [!info] 部署思路
> OpenClaw 的核心卖点就是"能够操作电脑文件、跑命令、整理资料",所以它设计上就是要访问文件的。但是如果让 OpenClaw 直接部署在宿主机(使用者常用的 Windows 环境)中,存在很高的安全风险,因此需要通过 WSL 进行隔离部署。

架构概览

</font>

## <font size=3>部署前准备

### <font size=2>step1: 安装 WSL 与系统依赖

<font size=2>

</font>

### <font size=2>step2: 安装 OpenClaw CLI

<font size=2>

> [!tip] 💡 安装后首次配置
> 安装完成后建议运行 openclaw onboard 进入交互式向导，自动完成基础配置。
> 向导会引导你设置 provider API key、channel 等核心项。

</font>

### <font size=2>step3: 验证网关状态

<font size=2>

</font>

## <font size=3>修改环境配置

### <font size=2>挂载 Windows 的路径

#### <font size=2>step1: 修改 wsl.conf 文件

<font size=2>

> [!caution] 🔥 注意
> default=whites 需要替换为你自己 WSL 中的实际用户名。可通过 whoami 命令查看。
> 修改后需重启 WSL 生效：wsl --shutdown 然后重新打开。

</font>

#### <font size=2>step2: 配置 openclaw.json

<font size=2>

> [!tip] 💡 配置文件位置
> ~/.openclaw/openclaw.json
> 可通过 openclaw config file 查看完整路径。

以下为 2026.9.4 版本的完整配置示例，按模块说明：

#### 2.1 核心代理配置 (agents)

> [!info] agents.entries 是 2026.9.x 的多 Agent 配置结构
> 2026.9.4 版本支持通过 `openclaw agents add <name> --workspace <dir>` 命令注册独立 Agent。
> 每个 Agent 拥有独立的 workspace、agentDir、identity 和 model 配置。
> `agents.ownership: "explicit"` 表示 Agent 归属关系显式声明。
>
> **当前部署架构（6 Agent，main 统一调度）**：
>
> | Agent | Workspace | Model | Routing |
> |-------|-----------|-------|---------|
> | main | ~/.openclaw/workspace | xiaomi/mimo-x-pro-preview | Feishu * (全量路由) |
> | coder | workspace/agents/coder | xiaomi/mimo-x-pro-preview | 0 (由 main 调度) |
> | clerk | workspace/agents/clerk | xiaomi/mimo-x-pro-preview | 0 |
> | evaluator | workspace/agents/evaluator | xiaomi/mimo-x-pro-preview | 0 |
> | secretary | workspace/agents/secretary | xiaomi/mimo-x-pro-preview | 0 |
> | analyst | workspace/agents/analyst | xiaomi/mimo-x-pro-preview | 0 |
>
> **注册命令示例**：
> ```bash
> openclaw agents add coder --workspace ~/.openclaw/workspace/agents/coder \
>   --non-interactive --model xiaomi/mimo-x-pro-preview
> ```
>
> **调度模式**：main 作为主控 Agent，通过 `sessions_send` / `sessions_spawn` 调度子 Agent，
> 子 Agent 不绑定独立飞书路由，统一由 main 接收消息并分发。
>
> **新增配置字段（2026.9.x）**：
> - `agents.defaults.systemAgent.agentId`: 系统事件处理 Agent
> - `agents.defaults.heartbeat.agentId`: 心跳轮询 Agent
> - `agents.ownership`: Agent 归属模式（explicit）

#### 2.2 网关配置 (gateway)

#### 2.3 工具与执行配置 (tools)

#### 2.4 认证与模型供应商 (auth + models)

> [!tip] 💡 模型供应商说明（2026.9.4 当前配置）
> - **xiaomi（计费接口）**：baseUrl=`https://api.xiaomimimo.com/v1`，模型 `mimo-x-pro-preview`，
>   上下文窗口 1M (1048576 tokens)，支持 reasoning，OpenAI 兼容格式
> - **xiaomi-token-plan（Token Plan）**：baseUrl=`https://token-plan-cn.xiaomimimo.com/v1`，
>   模型 `mimo-v2.5-pro`，国内免费额度，适合日常使用
>
> **双 Provider 配置结构**：
> - `models.mode: "merge"` — 合并模式，自定义 provider 与内置模型共存
> - `auth.profiles` — 每个 provider 对应一个认证 profile（mode: api_key）
> - `models.providers.<name>.apiKey` — 支持引用 OpenClaw secrets store（source: store）
>
> 当前默认模型：`xiaomi/mimo-x-pro-preview`（计费接口，1M 上下文）

#### 2.5 频道配置 (channels)

> [!caution] 🔥 安全提醒
> token、appSecret、botToken、apiKey 等敏感字段请替换为自己的值，不要直接使用示例中的占位符。
> 也不要将包含真实密钥的配置文件提交到 Git 仓库。

</font>

#### 2.6 插件与 Hooks (plugins + hooks)

<font size=2>

> [!info] 配置模块说明（2026.9.4）
> - plugins: 各供应商插件（anthropic、codex、xiaomi、feishu），通过 `plugins.entries` 管理
> - hooks: 内部钩子，`hooks.internal.entries` 中 `session-memory: { "enabled": true }` 自动加载会话记忆
> - meta: `meta.migrations.modelPolicyAllowlist: true` 记录模型策略迁移状态；`meta.lastTouchedVersion` 记录最后修改版本
> - commands: `commands.ownerAllowFrom` 指定允许执行管理命令的飞书用户 ID 列表

</font>

#### 2.7 Session 与路由配置

<font size=2>

2026.9.4 的 Session 和路由相关配置：

- `bindings`: 路由绑定数组，当前配置 `[{ "agentId": "main", "match": { "channel": "feishu", "accountId": "*" } }]` 表示飞书全量路由到 main Agent
- `talk.agentId`: 默认对话 Agent，当前为 `main`
- `commands.ownerAllowFrom`: Owner 命令白名单，限定飞书用户 ou_... 可执行管理命令

</font>

#### 2.8 记忆与向量检索 (memory)

<font size=2>

2026.9.4 新增 `memory.search` 配置模块，支持 embedding 向量语义检索：

- `memory.search.provider`: 使用 `openai-compatible` 协议
- `memory.search.remote.baseUrl`: 本地 embedding 服务地址（如 `http://127.0.0.1:18800/v1`）
- `memory.search.model`: embedding 模型名称（如 `embedding-2`）

配套的 `hooks.internal.entries.session-memory: { "enabled": true }` 确保每次会话自动加载记忆上下文。

</font>

---

## <font size=3>安装辅助工具

### <font size=2>ClawMetry（可选）

<font size=2>

> [!tip] 💡 可选组件
> ClawMetry 是专为 OpenClaw 设计的开源实时监控面板，按需安装。


区别于 Windows Docker Desktop+WSL+Ubuntu本地部署.md 描述的配置方法，由于不是在 Docker 中进行的部署，执行 pip install clawmetry 会报错，Python 环境被系统标记为 externally-managed-environment（PEP 668 保护机制），不允许直接用 pip 修改系统 Python。

通俗解释: 从 Python 3.11 开始，系统自带的 Python（通过 apt install python3 安装的）被标记为"由系统外部管理"。意思就是，操作系统（apt）才是这个 Python 的"主人"，不允许直接用 pip install 随意安装或升级包。如果直接执行 pip install xxx，系统就会抛出这个错误：

解决办法: 使用 pipx 代替 pip，它会为每个工具创建独立的虚拟环境。

</font>

### <font size=2>Karpathy LLM 知识库

<font size=2>

Karpathy LLM Skill（也常称为 Karpathy LLM Wiki 或 Karpathy-style LLM Knowledge Base）并不是一个单一的软件包，而是一个模式（pattern）+ 可安装的 Agent Skill。它的核心想法是：让 LLM（尤其是 Claude Code、Cursor、OpenClaw 等）自动把你的原始资料（文章、论文、图片等）编译成一个结构化的 Markdown Wiki（知识库），并持续维护、链接、更新它。人类只负责扔原始资料和提问，LLM 负责整理和合成知识。

这里我们运用他的核心思想来搭建自己的私人知识库，建议针对不同的领域，创建不同的 Vault。

Skill 配置

知识库目录是纯 Markdown 文件，而 OpenClaw 需要通过 Skill 来知道如何使用和管理它们。

</font>

### <font size=2>OpenSpace（可选）

<font size=2>

> [!tip] 💡 可选组件
> OpenSpace 是 OpenClaw 的全栈自主任务执行引擎，按需安装。通过 MCP Server 接入，支持编码、DevOps、Web 搜索、桌面自动化等能力，内置技能库可自动进化。

安装

使用途径 1：MCP 集成

在 openclaw.json 中添加 MCP 配置，让 OpenClaw 能"看到"并使用 OpenSpace 的工具。

使用途径 2：直接使用工具

OpenSpace 提供了几个强大工具，例如：

- execute_task（执行复杂多步任务）
- delegate-task（任务委派）
- skill-discovery（技能发现与演化）

启动后端（手动）

启动前端（手动）

启动前后端（自动脚本）

</font>

### <font size=2>OpenSpace MCP 自启动配置（SSE 模式 + systemd）

<font size=2>

> [!info] 背景说明
> 默认的 command: "openspace-mcp" 使用 stdio 模式，每次调用时启动进程，存在超时和冷启动问题。
> 推荐使用 SSE 模式：OpenSpace 作为常驻后台服务运行，OpenClaw 通过 HTTP 连接，无冷启动开销。
> 自启动方式采用 systemd user service（而非 OpenClaw hook），更可靠、支持开机自启和崩溃重启。

step1: 修改 openclaw.json 中的 MCP 配置

> [!tip] 💡 字段说明
> - transport: 固定为 sse
> - url: SSE 服务地址，端口可自定义（如 8080/8081）
> - toolTimeout: 单次工具调用超时（秒），建议 3600（1小时），复杂任务需要更长时间

step2: 创建 systemd user service

> [!tip] 💡 字段说明
> - ExecStart: 指向 openspace-mcp 的实际路径（可通过 which openspace-mcp 查看）
> - Restart=on-failure: 崩溃后自动重启
> - RestartSec=5: 重启间隔 5 秒
> - 日志输出到文件而非 stdout，方便排查

step3: 启用并启动服务

> [!info] WSL 中的 linger
> WSL 默认不保持 user session，loginctl enable-linger 确保 systemd user service
> 在 WSL 启动后自动运行，无需手动登录。

step4: 验证

常用运维命令

> [!caution] 🔥 注意事项
> - SSE 模式下 openspace-mcp 作为常驻进程运行，占用内存约 60-200MB
> - 端口（8081）需与 openclaw.json 中 mcp.servers.openspace.url 一致
> - OpenClaw hook 中的 openspace-autostart 应设置为 enabled: false（已由 systemd 管理）
> - ExecStart 路径需指向实际安装位置，可通过 which openspace-mcp 确认

</font>

### <font size=2>Obsidian

<font size=2>

Obsidian 作为本地 Markdown 知识库编辑器，配合 OpenClaw 使用。

- 用途：编辑和查看 Karpathy LLM Wiki 知识库、OpenClaw 部署笔记等
- 安装：在 Windows 侧安装 Obsidian 客户端，打开 WSL 挂载的目录（如 \\wsl$\Ubuntu-22.04\home\whites\Knowledge-LLM-Wiki\）
- 与 WSL 的交互：通过 /mnt/i/ 等挂载路径，OpenClaw Agent 可直接读写 Obsidian Vault 中的文件

</font>

### <font size=2>Claude Code + 小米 API 本地代理

<font size=2>

Claude Code 是 Anthropic 官方终端编程智能体，通过本地 Node.js 代理路由到小米 API，可免去 Anthropic 账号登录。

**架构**：
```
Claude Code → localhost:3000 (Node.js Proxy) → 按 model 字段分流
├─ mimo-v2.5* → token-plan-cn.xiaomimimo.com/anthropic (Anthropic 格式透传)
└─ mimo-x-pro-preview → api.xiaomimimo.com/v1/chat/completions (Anthropic→OpenAI 格式转换)
```

**安装 Claude Code**：
```bash
npm config set registry https://registry.npmmirror.com
npm install -g @anthropic-ai/claude-code
npm config set registry https://registry.npmjs.org
```

**代理服务器**：位于 `~/.openclaw/workspace/xiaomi-proxy/`
```bash
# 启动代理（自动加载 .env 中的 API Key）
cd ~/.openclaw/workspace/xiaomi-proxy && bash start.sh

# 验证代理健康
curl http://127.0.0.1:3000/health
```

**Claude Code 配置**（`~/.claude/settings.json`）：
```json
{
  "apiBaseUrl": "http://127.0.0.1:3000",
  "model": "mimo-v2.5-pro",
  "modelPicker": {
    "options": [
      { "model": "mimo-v2.5-pro", "label": "MiMo V2.5 Pro (Token Plan)", "behavesAs": "claude-sonnet-5" },
      { "model": "mimo-x-pro-preview", "label": "MiMo X Pro Preview (Billing)", "behavesAs": "claude-sonnet-5" }
    ]
  }
}
```

**环境变量**（wrapper 脚本 `~/.local/bin/claude`）：
```bash
export ANTHROPIC_API_KEY=***
export ANTHROPIC_BASE_URL="http://127.0.0.1:3000"
export CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1
export CLAUDE_CODE_MAX_CONTEXT_TOKENS=1000000
```

**使用**：
```bash
claude                                    # 交互模式
claude --model mimo-x-pro-preview         # 指定模型
claude --print "your question"             # 单次调用
```

> [!tip] 💡 关键配置说明
> - 代理的 `modelPicker.behavesAs` 字段让 Claude Code 将自定义模型映射为已知模型的 prompt profile
> - `CLAUDE_CODE_MAX_CONTEXT_TOKENS=1000000` 对应小米模型 1M 上下文窗口
> - 代理需使用 `bash start.sh` 启动（会加载 `.env` 中的 Key），直接 `node server.js` 会导致 Key 缺失
> - Anthropic→OpenAI 格式转换包括：messages 结构映射、system prompt 处理、SSE 流式响应转换

</font>

### <font size=2>GitHub CLI (gh)

<font size=2>

GitHub CLI 用于 PR、Issue、CI 等 GitHub 操作，是 github 和 gh-issues Skill 的依赖工具。

**安装（无需 sudo，用户级安装）**：
```bash
curl -sL https://github.com/cli/cli/releases/download/v2.74.2/gh_2.74.2_linux_amd64.tar.gz \
  -o /tmp/gh.tar.gz && tar -xzf /tmp/gh.tar.gz -C /tmp
mkdir -p ~/.local/bin && cp /tmp/gh_2.74.2_linux_amd64/bin/gh ~/.local/bin/
```

**SSH Key 配置**：
```bash
ssh-keyscan github.com >> ~/.ssh/known_hosts
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_ed25519 -N ""
# 将 ~/.ssh/id_ed25519.pub 添加到 GitHub → Settings → SSH Keys
ssh -T git@github.com  # 验证
```

**Token 认证**：
```bash
# 在 GitHub Settings → Tokens 创建 PAT (classic)，勾选 repo, read:org, workflow
mkdir -p ~/.config/gh
cat > ~/.config/gh/hosts.yml << 'EOF'
github.com:
    user: <your_username>
    oauth_token: <your_token>
    git_protocol: ssh
EOF
chmod 600 ~/.config/gh/hosts.yml
```

**Git 全局配置**：
```bash
git config --global user.name "<your_username>"
git config --global user.email "<your_email>"
git config --global credential.helper store
```

**验证**：
```bash
gh auth status
```

> [!tip] 💡 注意事项
> - Go 编译的 gh CLI 使用内置 DNS 解析器，WSL2 需确保 `/etc/resolv.conf` 包含公共 DNS（如 `8.8.8.8`）
> - Token 权限要求：Fine-grained PAT 需勾选 Contents (R/W)、Metadata (R)、Pull requests (R/W)、Issues (R/W)
> - SSH + Token 双认证：git 操作走 SSH，gh API 调用走 Token

</font>

### <font size=2>自定义 Skills

<font size=2>

OpenClaw 自定义 Skills 放在 ~/.openclaw/workspace/skills/ 目录下，系统自动发现并加载。

当前已配置的自定义 Skills：

| Skill                    | 用途                                       |
| ------------------------ | ------------------------------------------ |
| `cms32-series-embedded` | 中微 CMS32/CMS8S 8051 嵌入式开发工作流    |
| `embedded-llm-wiki`      | 嵌入式知识库（Karpathy 风格，raw→wiki）    |
| `embedded-workspace`     | 嵌入式工作区公约（embedded_lib 只读隔离）  |
| `impeccable-uxui`        | UI/UX 设计语言参考（前端设计规范）         |
| `md-frontmatter-table`   | Markdown Frontmatter 表格生成              |
| `stm32-rt-thread`        | STM32 + RT-Thread 开发工作流               |
| `stm32-spl-bare-metal`   | STM32 SPL 裸机开发工作流                   |

**workshop-skills**（`~/.openclaw/agents/main/agent/workshop-skills/`）：

| Skill                        | 用途                                 |
| ---------------------------- | ------------------------------------ |
| `claude-code-api-proxy`      | Claude Code 本地 API 代理配置        |
| `udx-version-management`     | UDS OTA 项目版本号管理               |

> [!info] Skills 加载优先级
> 自定义 Skills > 内置 Skills（npm 包内） > 飞书扩展 Skills。同名 Skill 自定义优先覆盖。

</font>

---

## <font size=3>常用运维命令速查

<font size=2>

</font>

---

## <font size=3>版本兼容性说明（2026.4.x → 2026.9.x）

<font size=2>

| 特性                              | 2026.4.x | 2026.9.4 | 说明                                     |
| --------------------------------- | -------- | -------- | ---------------------------------------- |
| `agents.entries` 多 Agent        | ❌       | ✅       | 2026.9.x 新增，`openclaw agents add` 注册 |
| `agents.ownership`               | ❌       | ✅       | Agent 归属模式（explicit）               |
| `agents.defaults.systemAgent`    | ❌       | ✅       | 系统事件处理 Agent 指定                  |
| `agents.defaults.heartbeat`      | ❌       | ✅       | 心跳轮询 Agent 指定                      |
| `models.providers` 自定义供应商  | ✅       | ✅       | 支持 xiaomi billing + token-plan 双路由  |
| `memory.search` 向量检索         | ✅       | ✅       | provider=openai-compatible, embedding-2  |
| `hooks.internal` 内部钩子        | ✅       | ✅       | session-memory 等                        |
| `mcp.servers` MCP 集成           | ✅       | ✅       | 支持 stdio / sse 两种模式                |
| `bindings` 路由绑定              | ✅       | ✅       | 按 channel + accountId 路由到 Agent      |
| `plugins.entries`                | ✅       | ✅       | anthropic/codex/xiaomi/feishu            |
| `meta.migrations`                | ❌       | ✅       | 配置迁移标记（modelPolicyAllowlist）      |
| `commands.ownerAllowFrom`        | ❌       | ✅       | 命令白名单（飞书用户 ID）                |
| `models.mode: "merge"`           | ❌       | ✅       | 自定义与内置模型合并模式                 |
| `modelPicker` (Claude Code)      | ❌       | ✅       | 自定义模型映射（behavesAs）              |
| `tools.exec.host: "gateway"`     | ✅       | ✅       | gateway 模式可访问挂载盘                 |
| `wizard` 自动配置记录            | ✅       | ✅       | 自动维护，无需手动设置                   |

> [!tip] 💡 升级提示
> 从旧版本升级到 2026.9.4：`openclaw update`
> 升级后建议运行 `openclaw onboard` 重新完成向导配置。
> 多 Agent 注册：`openclaw agents add <name> --workspace <dir> --non-interactive --model <model>`
> 配置文件结构向下兼容，旧配置通常无需修改即可运行。

</font>

---

## <font size=3>变更记录

<font size=2>

| 版本     | 日期       | 主要改动点                                                             |
| -------- | ---------- | ---------------------------------------------------------------------- |
| 2026.4.22 | 2026-05-16 | 初始版本，基于 OpenClaw 2026.4.22 + Ubuntu 24.04.4 LTS                |
| 2026.9.4  | 2026-09-20 | 更新至 OpenClaw 2026.9.4 + Ubuntu 26.04；新增多 Agent 架构说明；更新模型供应商为 xiaomi 双 provider；Claude Code 章节改为小米 API 本地代理方案；GitHub CLI 补充 SSH+Token 双认证；更新 Skills 列表；新增版本兼容性对比 |

</font>
