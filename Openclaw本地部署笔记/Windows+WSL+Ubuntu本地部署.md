---
tags:
  - openclaw
created: 2026-04-02 18:19:00
updated: 2026-04-30 05:16
---

# <font size=4>Windows + WSL + Ubuntu + OpenClaw 本地部署</font>

> [!info] 版本说明
> 本文档基于 **OpenClaw 2026.4.22** 编写，适用于 2026.4.x 系列版本。
> 安装前请确认最新版本：`openclaw --version`

## <font size=3>简要概述</font>

<font size=2>

> [!info] 部署思路
> OpenClaw 的核心卖点就是"能够操作电脑文件、跑命令、整理资料",所以它设计上就是要访问文件的。但是如果让 OpenClaw 直接部署在宿主机(使用者常用的 Windows 环境)中,存在很高的安全风险,因此需要通过 WSL 进行隔离部署。

**架构概览**

```
Windows 11 宿主机
  └── WSL2 (Ubuntu 22.04)
        ├── Node.js v22.x
        ├── OpenClaw Gateway (127.0.0.1:18789)
        ├── 多 Agent 系统 (main / coder / evaluator / analyst / secretary / clerk)
        └── 可选: OpenSpace MCP, ClawMetry 等辅助工具
```

</font>

## <font size=3>部署前准备</font>

### <font size=2>step1: 安装 WSL 与系统依赖</font>

<font size=2>

```bash
# 1. 查看已安装的 WSL 发行版
wsl --list --verbose

# 2. 查看可安装的发行版列表
wsl --list --online

# 3. 删除 WSL 虚拟机（如需重装）
# 3.1 先关闭 WSL
wsl --shutdown

# 3.2 卸载(删除)指定发行版
wsl --unregister Ubuntu-22.04

# 4. 安装特定版本(例如 Ubuntu 22.04)
wsl --install -d Ubuntu-22.04

# 5. 设置 Ubuntu 为默认打开
wsl --setdefault Ubuntu-22.04

# 6. 更新安装工具
sudo apt update && sudo apt upgrade -y

# 7. 安装 curl、git 等基础工具
sudo apt install curl git build-essential -y

# 8. 安装 Node.js (OpenClaw 依赖 Node.js ≥22)
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# 9. 验证
node --version   # 应该显示 v22.x 或更高
npm --version
```

</font>

### <font size=2>step2: 安装 OpenClaw CLI</font>

<font size=2>

```bash
# 一键安装（推荐）
curl -fsSL https://openclaw.ai/install.sh | bash

# 如果一键安装失败，手动安装：
# npm install -g openclaw

# 修复 PATH（确保 openclaw 命令可用）
# 1. 查看 npm 全局安装位置
npm config get prefix

# 2. 自动适配 prefix 添加到 PATH
echo 'export PATH="$(npm config get prefix)/bin:$PATH"' >> ~/.bashrc

# 3. 使配置生效
source ~/.bashrc
hash -r

# 4. 验证安装
openclaw --version   # 应显示如: OpenClaw 2026.4.22

# 5. 启动网关
openclaw gateway start
```

> [!tip] 安装后首次配置
> 安装完成后建议运行 `openclaw onboard` 进入交互式向导，自动完成基础配置。
> 向导会引导你设置 provider API key、channel 等核心项。

</font>

### <font size=2>step3: 验证网关状态</font>

<font size=2>

```bash
# 检查网关运行状态
openclaw gateway status

# 检查整体状态
openclaw status

# 访问控制面板
# 浏览器打开: http://127.0.0.1:18789/
```

</font>

## <font size=3>修改环境配置</font>

### <font size=2>挂载 Windows 的路径</font>

#### <font size=2>step1: 修改 wsl.conf 文件</font>

<font size=2>

```bash
# 进入 /etc/wsl.conf 文件
sudo nano /etc/wsl.conf

# 修改内容
```

```ini
[boot]
systemd=true

# 注意: user 改为你的 WSL 用户名（可通过 whoami 查看）
[user]
default=whites

[automount]
enabled=true
root=/mnt/
options=metadata,uid=1000,gid=1000,umask=0022,fmask=011,case=off

[interop]
enabled=true
appendWindowsPath=true
```

> [!caution] 注意
> `default=whites` 需要替换为你自己 WSL 中的实际用户名。可通过 `whoami` 命令查看。
> 修改后需重启 WSL 生效：`wsl --shutdown` 然后重新打开。

</font>

#### <font size=2>step2: 配置 openclaw.json</font>

<font size=2>

> [!tip] 配置文件位置
> `~/.openclaw/openclaw.json`
> 可通过 `openclaw config file` 查看完整路径。

**以下为 2026.4.22 版本的完整配置示例，按模块说明：**

#### 2.1 核心代理配置 (agents)

```jsonc
{
  "agents": {
    "defaults": {
      "workspace": "/home/whites/.openclaw/workspace",
      "sandbox": { "mode": "off" },

      // 记忆搜索（向量检索）
      "memorySearch": {
        "enabled": true,
        "provider": "openai",
        "model": "embedding-3",
        "remote": {
          "baseUrl": "https://open.bigmodel.cn/api/paas/v4",
          "apiKey": "<你的智谱API Key>"
        },
        "cache": { "enabled": true }
      },

      // 可用模型列表（别名映射）
      "models": {
        "xiaomi/mimo-v2-omni": { "alias": "mimo-v2-omni" },
        "xiaomi/mimo-v2-pro": { "alias": "mimo-v2-pro" },
        "zai/glm-4.1v-thinking-flashx": { "alias": "GLM-4.1V-Thinking-FlashX" },
        "moonshot/kimi-2.5": { "alias": "Kimi-2.5" },
        "openrouter/xiaomi/mimo-v2-pro": { "alias": "openrouter/xiaomi/mimo-v2-pro" },
        "x-ai/grok-4.1-fast": { "alias": "x-ai/grok-4.1-fast" }
      },

      "subagents": { "maxConcurrent": 5 },

      // 默认主模型
      "model": { "primary": "xiaomi/mimo-v2-pro" }
    },

    // 多 Agent 定义（2026.4.x 新结构）
    "list": [
      {
        "id": "main",
        "default": true,
        "name": "Main Coordinator",
        "workspace": "/home/whites/.openclaw/workspace",
        "model": {
          "primary": "xiaomi/mimo-v2-pro",
          "fallbacks": ["x-ai/grok-4.1-fast", "moonshot/kimi-2.5"]
        },
        "subagents": {
          "allowAgents": ["secretary", "coder", "evaluator", "analyst"]
        }
      },
      {
        "id": "secretary",
        "name": "Secretary",
        "workspace": "/home/whites/.openclaw/workspace/agents/secretary",
        "model": {
          "primary": "x-ai/grok-4.1-fast",
          "fallbacks": ["xiaomi/mimo-v2-pro", "moonshot/kimi-2.5"]
        },
        "tools": {
          "allow": ["calendar", "email", "reminder", "web_search", "read", "write", "exec"],
          "deny": ["agentToAgent", "sessions_send", "sessions_spawn", "code_exec", "git", "finance_api"],
          "exec": { "security": "full" },
          "fs": { "workspaceOnly": false }
        }
      },
      {
        "id": "coder",
        "name": "Coder",
        "workspace": "/home/whites/.openclaw/workspace/agents/coder",
        "model": {
          "primary": "openrouter/xiaomi/mimo-v2-pro",
          "fallbacks": ["x-ai/grok-4.1-fast", "xiaomi/mimo-v2-pro", "moonshot/kimi-2.5"]
        }
      },
      {
        "id": "evaluator",
        "name": "Evaluator",
        "workspace": "/home/whites/.openclaw/workspace/agents/evaluator",
        "model": {
          "primary": "moonshot/kimi-2.5",
          "fallbacks": ["xiaomi/mimo-v2-pro"]
        }
      },
      {
        "id": "analyst",
        "name": "Analyst",
        "workspace": "/home/whites/.openclaw/workspace/agents/analyst",
        "model": {
          "primary": "xiaomi/mimo-v2-omni",
          "fallbacks": ["moonshot/kimi-2.5", "xiaomi/mimo-v2-pro"]
        }
      }
    ]
  }
}
```

> [!info] agents.list 是 2026.4.x 的新结构
> 旧版本使用 `agents.defaults` 集中配置，2026.4.x 支持通过 `agents.list` 定义多个独立 Agent，
> 每个 Agent 可以有独立的 workspace、model、tools 权限和 fallback 链。

#### 2.2 网关配置 (gateway)

```jsonc
{
  "gateway": {
    "mode": "local",
    "auth": {
      "mode": "token",
      "token": "<自动生成的token，首次 onboard 后生成>"
    },
    "port": 18789,
    "bind": "loopback",
    "tailscale": {
      "mode": "off",
      "resetOnExit": false
    },
    "controlUi": {
      "allowInsecureAuth": false
    },
    "nodes": {
      "denyCommands": [
        "camera.snap", "camera.clip", "camera.list",
        "screen.record",
        "contacts.add", "calendar.add", "reminders.add", "reminders.list",
        "sms.send", "sms.search"
      ]
    }
  }
}
```

#### 2.3 工具与执行配置 (tools)

```jsonc
{
  "tools": {
    "profile": "full",
    "allow": ["*"],
    "exec": {
      "host": "gateway",           // 关键! gateway 模式可访问 Windows 挂载盘
      "security": "full",          // 完全权限（生产环境建议改为 allowlist）
      "ask": "off"                 // 关闭审批（调试期），稳定后改为 "on"
    },
    "web": {
      "search": {
        "provider": "grok",
        "enabled": true
      },
      "x_search": {
        "enabled": true,
        "model": "grok-4-1-fast"
      }
    }
  }
}
```

#### 2.4 认证与模型供应商 (auth + models)

```jsonc
{
  "auth": {
    "profiles": {
      "openrouter:default": { "provider": "openrouter", "mode": "api_key" },
      "moonshot:default":   { "provider": "moonshot",   "mode": "api_key" },
      "xiaomi:default":     { "provider": "xiaomi",     "mode": "api_key" },
      "zai:default":        { "provider": "zai",        "mode": "api_key" }
    }
  },

  "models": {
    "mode": "merge",
    "providers": {
      "moonshot": {
        "baseUrl": "https://api.moonshot.cn/v1",
        "api": "openai-completions",
        "models": [
          {
            "id": "kimi-k2.5",
            "name": "Kimi K2.5",
            "reasoning": false,
            "input": ["text", "image"],
            "contextWindow": 262144,
            "maxTokens": 262144
          }
        ]
      },
      "xiaomi": {
        "baseUrl": "https://api.xiaomimimo.com/v1",
        "api": "openai-completions",
        "models": [
          {
            "id": "mimo-v2-flash",
            "name": "Xiaomi MiMo V2 Flash",
            "reasoning": true,
            "input": ["text"],
            "contextWindow": 262144,
            "maxTokens": 8192
          },
          {
            "id": "mimo-v2-pro",
            "name": "Xiaomi MiMo V2 Pro",
            "reasoning": true,
            "input": ["text"],
            "contextWindow": 1048576,
            "maxTokens": 32000
          },
          {
            "id": "mimo-v2-omni",
            "name": "Xiaomi MiMo V2 Omni",
            "reasoning": true,
            "input": ["text", "image"],
            "contextWindow": 262144,
            "maxTokens": 32000
          }
        ]
      },
      "zai": {
        "baseUrl": "https://open.bigmodel.cn/api/paas/v4",
        "api": "openai-completions",
        "models": [
          {
            "id": "glm-4.7-flashx",
            "name": "GLM-4.7 FlashX",
            "reasoning": true,
            "input": ["text"],
            "contextWindow": 200000,
            "maxTokens": 128000
          },
          {
            "id": "glm-4.6v",
            "name": "GLM-4.6V",
            "reasoning": true,
            "input": ["text", "image"],
            "contextWindow": 128000,
            "maxTokens": 32768
          }
        ]
      }
    }
  }
}
```

> [!tip] 模型供应商说明
> - **xiaomi**: 小米 MiMo 系列，国内免费额度，适合日常使用
> - **moonshot**: 月之暗面 Kimi 系列，长上下文
> - **zai (智谱)**: GLM 系列，同时提供 embedding 模型用于记忆搜索
> - **openrouter**: 聚合路由，可访问多家模型（需要余额）
> - **x-ai**: Grok 系列，用于 web search 和 x_search

#### 2.5 频道配置 (channels)

```jsonc
{
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "<飞书应用 App ID>",
      "appSecret": "<飞书应用 App Secret>",
      "connectionMode": "websocket",
      "domain": "feishu",
      "groupPolicy": "allowlist"          // allowlist | open | closed
    },
    "telegram": {
      "enabled": true,
      "groups": {
        "*": { "requireMention": true }
      },
      "botToken": "<Telegram Bot Token>"
    },
    "qqbot": {
      "enabled": false,
      "allowFrom": ["*"],
      "appId": "<QQ Bot App ID>",
      "clientSecret": "<QQ Bot Client Secret>"
    }
  }
}
```

> [!caution] 安全提醒
> `token`、`appSecret`、`botToken`、`apiKey` 等敏感字段请替换为自己的值，不要直接使用示例中的占位符。
> 也不要将包含真实密钥的配置文件提交到 Git 仓库。

</font>

#### 2.6 插件与 Hooks (plugins + hooks)

<font size=2>

```jsonc
{
  "plugins": {
    "entries": {
      "xai": {
        "enabled": true,
        "config": {
          "webSearch": { "apiKey": "<xAI API Key>" },
          "xSearch": { "enabled": true, "model": "grok-4-1-fast" }
        }
      },
      "feishu": { "enabled": true },
      "xiaomi": { "enabled": true },
      "openrouter": { "enabled": true },
      "moonshot": { "enabled": true },
      "memory-core": {
        "config": {
          "dreaming": { "enabled": true }
        }
      },
      "zai": { "enabled": true }
    }
  },

  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "boot-md": { "enabled": true },
        "bootstrap-extra-files": { "enabled": true },
        "command-logger": { "enabled": true },
        "session-memory": { "enabled": true }
      }
    }
  },

  "skills": {
    "load": {
      "extraDirs": ["/home/whites/.openclaw/workspace/skills"]
    }
  },

  "bindings": [
    {
      "type": "route",
      "agentId": "main",
      "match": { "channel": "feishu" }
    },
    {
      "type": "route",
      "agentId": "secretary",
      "match": { "channel": "telegram" }
    }
  ]
}
```

> [!info] 新增配置模块说明（2026.4.x）
> - **plugins**: 各供应商插件 + memory-core（记忆/梦境功能）
> - **hooks**: 内部钩子，agent bootstrap 时自动执行（如 session-memory 自动加载记忆）
> - **skills**: 额外技能目录，Agent 可自动发现并使用
> - **bindings**: 路由绑定，指定哪个 channel 的消息路由到哪个 Agent

</font>

#### 2.7 Session 配置

<font size=2>

```jsonc
{
  "session": {
    "dmScope": "per-channel-peer"   // 每个 channel+用户 对应独立会话
  }
}
```

</font>

---

## <font size=3>安装辅助工具</font>

### <font size=2>ClawMetry</font>

<font size=2>

ClawMetry 是专为 OpenClaw 设计的开源实时监控面板。

```bash
# 安装
pipx install clawmetry

# 检查 clawmetry 是否真的装好
ls ~/.local/bin/clawmetry

# 把 ~/.local/bin 加到 PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 启动(自动打开 localhost:8900)
clawmetry
```

![step1](./images/openclaw-widnows-5.png)

区别于 `Windows Docker Desktop+WSL+Ubuntu本地部署.md` 描述的配置方法，由于不是在 Docker 中进行的部署，执行 `pip install clawmetry` 会报错，Python 环境被系统标记为 `externally-managed-environment`（PEP 668 保护机制），不允许直接用 pip 修改系统 Python。

**通俗解释:** 从 Python 3.11 开始，系统自带的 Python（通过 apt install python3 安装的）被标记为"由系统外部管理"。意思就是，操作系统（apt）才是这个 Python 的"主人"，不允许直接用 pip install 随意安装或升级包。如果直接执行 `pip install xxx`，系统就会抛出这个错误：

```bash
error: externally-managed-environment
× This environment is externally managed
```

**解决办法:** 使用 `pipx` 代替 `pip`，它会为每个工具创建独立的虚拟环境。

</font>

### <font size=2>Karpathy LLM 知识库</font>

<font size=2>

Karpathy LLM Skill（也常称为 Karpathy LLM Wiki 或 Karpathy-style LLM Knowledge Base）并不是一个单一的软件包，而是一个模式（pattern）+ 可安装的 Agent Skill。它的核心想法是：让 LLM（尤其是 Claude Code、Cursor、OpenClaw 等）自动把你的原始资料（文章、论文、图片等）编译成一个结构化的 Markdown Wiki（知识库），并持续维护、链接、更新它。人类只负责扔原始资料和提问，LLM 负责整理和合成知识。

这里我们运用他的核心思想来搭建自己的私人知识库，建议针对不同的领域，创建不同的 Vault。

```bash
# 目录结构示例

~/Knowledge-LLM-Wiki/                 ← 所有知识库的统一父目录
├── embedded/                         ← 嵌入式系统知识库
│   ├── raw/                          ← 原始资料
│   │   └── assets/                   ← 图片、PDF附件等
│   └── wiki/                         ← LLM 维护的结构化知识
│       ├── schema.md                 ← 规则文件
│       ├── index.md                  ← 总索引
│       ├── concepts/
│       ├── devices/
│       ├── protocols/
│       └── summaries/
│
└── ai/                               ← AI / LLM 知识库
    ├── raw/
    │   └── assets/
    └── wiki/
        ├── schema.md
        ├── index.md
        ├── concepts/
        ├── models/
        ├── techniques/
        └── summaries/
```

**Skill 配置**

知识库目录是纯 Markdown 文件，而 OpenClaw 需要通过 Skill 来知道如何使用和管理它们。

```bash
# Skill 目录结构（放在 OpenClaw 的 skills 目录下）
~/.openclaw/workspace/skills/
├── llm-wiki-embedded/           ← 嵌入式知识库专用 Skill
│   ├── SKILL.md                 ← 核心文件
│   └── README.md
│
└── llm-wiki-ai/                 ← AI 知识库专用 Skill
    ├── SKILL.md
    └── README.md
```

</font>

### <font size=2>OpenSpace</font>

<font size=2>

OpenSpace 是 OpenClaw 的全栈自主任务执行引擎，通过 MCP Server 接入，支持编码、DevOps、Web 搜索、桌面自动化等能力，内置技能库可自动进化。

**安装**

```bash
# 1. 克隆仓库
git clone https://github.com/HKUDS/OpenSpace.git
cd OpenSpace

# 2. 如果已经安装，需要升级（可选）
git pull

# 3. 安装（可编辑模式）
pipx install -e .

# 4. 验证安装是否成功
openspace-mcp --help
```

**使用途径 1：MCP 集成**

在 `openclaw.json` 中添加 MCP 配置，让 OpenClaw 能"看到"并使用 OpenSpace 的工具。

**使用途径 2：直接使用工具**

OpenSpace 提供了几个强大工具，例如：
- `execute_task`（执行复杂多步任务）
- `delegate-task`（任务委派）
- `skill-discovery`（技能发现与演化）

**启动后端（手动）**

```bash
openspace-dashboard --port 7788 --host 127.0.0.1

# 启动成功后会看到
Running on http://127.0.0.1:7788
```

**启动前端（手动）**

```bash
cd ~/OpenSpace/frontend

# 如果是第一次启动，需要安装依赖（只需执行一次）
npm install

# 启动前端开发服务器
npm run dev -- --host 127.0.0.1 --port 3789
```

**启动前后端（自动脚本）**

```bash
#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="/home/whites/OpenSpace/logs/openspace"
mkdir -p "$LOG_DIR"

echo "=== Starting OpenSpace with pipx ==="

# ---------- Backend ----------
if ss -tlnn | grep -q ":7788 "; then
  echo "✅ Dashboard backend already running on port 7788"
else
  nohup openspace-dashboard --port 7788 --host 0.0.0.0 \
    >"$LOG_DIR/dashboard.log" 2>&1 &
  echo "✅ Dashboard backend started (port 7788)"
fi

# ---------- Frontend ----------
FRONTEND_DIR="/home/whites/OpenSpace/frontend"
if [ ! -d "$FRONTEND_DIR" ]; then
  echo "❌ Frontend directory missing: $FRONTEND_DIR"
  exit 1
fi

if ss -tlnn | grep -q ":3789 "; then
  echo "✅ Frontend already running on port 3789"
else
  cd "$FRONTEND_DIR"
  npm ci >"$LOG_DIR/npm-install.log" 2>&1 || {
    echo "❌ npm dependencies 安装失败，查看 $LOG_DIR/npm-install.log"
    exit 1
  }
  nohup npm run dev -- --host 0.0.0.0 --port 3789 \
    >"$LOG_DIR/frontend.log" 2>&1 &
  echo "✅ Frontend started (port 3789)"
fi

# ---------- 状态 ----------
echo "=== OpenSpace Status ==="
ss -tlnn | grep -E "7788|3789" || echo "⚠️ 未检测到监听端口"
echo "访问地址: http://127.0.0.1:3789"
```

</font>

### <font size=2>OpenSpace MCP 自启动配置（SSE 模式）</font>

<font size=2>

> [!info] 背景说明
> 默认的 `command: "openspace-mcp"` 使用 stdio 模式，每次调用时启动进程，存在超时和冷启动问题。
> 推荐使用 SSE 模式：OpenSpace 作为常驻后台服务运行，OpenClaw 通过 HTTP 连接，无冷启动开销。

**step1: 修改 openclaw.json 中的 MCP 配置**

```json
{
  "mcp": {
    "servers": {
      "openspace": {
        "enabled": true,
        "transport": "sse",
        "url": "http://127.0.0.1:8081/sse",
        "toolTimeout": 3600
      }
    }
  }
}
```

> [!tip] 字段说明
> - `transport`: 固定为 `sse`
> - `url`: SSE 服务地址，端口可自定义（如 8080/8081）
> - `toolTimeout`: 单次工具调用超时（秒），建议 3600（1小时），复杂任务需要更长时间

**step2: 创建 OpenClaw Hook 实现自启动**

```bash
# 创建 hook 目录
mkdir -p ~/.openclaw/hooks/openspace-autostart
```

创建 `~/.openclaw/hooks/openspace-autostart/HOOK.md`：

```markdown
---
name: openspace-autostart
description: "Auto-start OpenSpace MCP server on agent bootstrap"
metadata:
  { "openclaw": { "emoji": "🌐", "events": ["agent:bootstrap"], "requires": {} } }
---

# OpenSpace Auto-Start

Starts openspace-mcp SSE server in background on agent bootstrap.
Transport: SSE on 127.0.0.1:8081
```

创建 `~/.openclaw/hooks/openspace-autostart/handler.ts`：

```typescript
const handler = async (event: any) => {
  if (event.type !== "agent:bootstrap") return;

  const { execSync, exec } = require("child_process");

  try {
    const check = execSync("pgrep -f 'openspace-mcp' 2>/dev/null", {
      encoding: "utf8",
      timeout: 3000
    }).trim();
    if (check) {
      console.log("[openspace-autostart] already running, pid=" + check);
      return;
    }
  } catch {
    // pgrep 返回非零 = 未找到进程，继续启动
  }

  try {
    exec(
      "nohup openspace-mcp --transport sse --host 127.0.0.1 --port 8081 > /home/whites/OpenSpace/logs/openspace/mcp-autostart.log 2>&1 &",
      (err: any) => {
        if (err) {
          console.error("[openspace-autostart] failed:", err.message);
        } else {
          console.log("[openspace-autostart] started on http://127.0.0.1:8081/sse");
        }
      }
    );
  } catch (e: any) {
    console.error("[openspace-autostart] error:", e.message);
  }
};

export default handler;
```

**step3: 在 openclaw.json 中注册 hook**

```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "boot-md": { "enabled": true },
        "openspace-autostart": { "enabled": true }
      }
    }
  }
}
```

**step4: 确保日志目录存在**

```bash
mkdir -p /home/whites/OpenSpace/logs/openspace
```

**step5: 验证**

```bash
# 手动测试启动
openspace-mcp --transport sse --host 127.0.0.1 --port 8081 &

# 检查是否监听
ss -tlnp | grep 8081

# 检查 SSE 端点是否响应
curl -s http://127.0.0.1:8081/sse | head -2
# 预期输出:
# event: endpoint
# data: /messages/?session_id=xxx

# 重启 OpenClaw gateway 测试自启动
openclaw gateway restart
# 等待几秒后检查
sleep 5 && pgrep -f openspace-mcp
```

> [!caution] 注意事项
> - SSE 模式下 `openspace-mcp` 作为常驻进程运行，占用内存约 100-200MB
> - 端口（8081）需与 `openclaw.json` 中 `mcp.servers.openspace.url` 一致
> - 如果需要停止 OpenSpace：`pkill -f openspace-mcp`
> - 日志文件：`/home/whites/OpenSpace/logs/openspace/mcp-autostart.log`

</font>

### <font size=2>Obsidian</font>

<font size=2>

Obsidian 作为本地 Markdown 知识库编辑器，配合 OpenClaw 使用。

- **用途**：编辑和查看 Karpathy LLM Wiki 知识库、OpenClaw 部署笔记等
- **安装**：在 Windows 侧安装 Obsidian 客户端，打开 WSL 挂载的目录（如 `\\wsl$\Ubuntu-22.04\home\whites\Knowledge-LLM-Wiki\`）
- **与 WSL 的交互**：通过 `/mnt/i/` 等挂载路径，OpenClaw Agent 可直接读写 Obsidian Vault 中的文件

</font>

---

## <font size=3>常用运维命令速查</font>

<font size=2>

```bash
# === 网关管理 ===
openclaw gateway start       # 启动网关
openclaw gateway stop        # 停止网关
openclaw gateway restart     # 重启网关
openclaw gateway status      # 查看网关状态

# === 状态检查 ===
openclaw status              # 整体状态概览
openclaw status --deep       # 深度检查（含 channel 测试）
openclaw doctor              # 健康检查 + 快速修复

# === 日志查看 ===
openclaw logs --follow       # 实时跟踪日志
openclaw logs --lines 100    # 查看最近 100 行

# === 配置管理 ===
openclaw config file         # 显示配置文件路径
openclaw config validate     # 验证配置语法
openclaw configure           # 交互式配置向导

# === 更新 ===
openclaw update              # 更新到最新版本
npm update -g openclaw       # 备用更新方式

# === 记忆管理 ===
openclaw memory              # 搜索和检查记忆

# === Cron 任务 ===
openclaw cron list           # 查看定时任务
openclaw cron logs           # 查看任务执行日志
```

</font>

---

## <font size=3>版本兼容性说明（2026.4.x 系列）</font>

<font size=2>

| 特性 | 2026.4.1 | 2026.4.22 | 说明 |
|------|----------|-----------|------|
| `agents.list` 多 Agent | ✅ | ✅ | 2026.4.x 新增，每个 Agent 独立配置 |
| `models.providers` 自定义供应商 | ✅ | ✅ | 支持 xiaomi/moonshot/zai 等 |
| `memorySearch` 向量检索 | ✅ | ✅ | 支持 openai 兼容 embedding |
| `hooks.internal` 内部钩子 | ✅ | ✅ | session-memory, boot-md 等 |
| `mcp.servers` MCP 集成 | ✅ | ✅ | 支持 stdio / sse 两种模式 |
| `skills.load.extraDirs` | ✅ | ✅ | 额外技能目录 |
| `bindings` 路由绑定 | ✅ | ✅ | 按 channel 路由到不同 Agent |
| `plugins.entries` | ✅ | ✅ | 各供应商 + memory-core 插件 |
| `tools.exec.host: "gateway"` | ✅ | ✅ | gateway 模式可访问挂载盘 |
| `wizard` 自动配置记录 | ✅ | ✅ | 自动维护，无需手动设置 |

> [!tip] 升级提示
> 从旧版本升级到 2026.4.22：`npm update -g openclaw` 或 `openclaw update`
> 升级后建议运行 `openclaw onboard` 重新完成向导配置。
> 配置文件结构向下兼容，旧配置通常无需修改即可运行。

</font>
