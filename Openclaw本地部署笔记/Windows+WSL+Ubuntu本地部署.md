---
tags:
  - openclaw
created: 2026-04-02 18:19:00
---

# <font size=4>Windows + WSL + Ubuntu + OpenClaw 本地部署</font>

## <font size=3>简要概述</font>

<font size=2>

> [!info] 部署思路
> OpenClaw 的核心卖点就是"能够操作电脑文件、跑命令、整理资料",所以它设计上就是要访问文件的。但是如果让 OpenClaw 直接部署在宿主机(使用者常用的 Windows 环境)中,存在很高的安全风险,因此需要通过 WSL 进行隔离部署。

</font>

## <font size=3>部署前准备</font>

### <font size=2>step1: 安装依赖</font>

<font size=2>

```bash
# 1. 查看已安装的 WSL 发行版
wsl --list --verbose

# 2. 查看可安装的发行版列表
wsl --list --online

# 3. 删除 WSL 虚拟机
# 3.1 先关闭 WSL
wsl --shutdown

# 3.2 卸载(删除)指定发行版
wsl --unregister Ubuntu-22.04

# 4. 查看可用的 Ubuntu 版本
wsl --list --online

# 4.1 安装特定版本(例如 Ubuntu 22.04)
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

### <font size=2>step2: 一键安装</font>

<font size=2>

```bash
# 推荐安装方式:一键脚本
curl -fsSL https://openclaw.ai/install.sh | bash
```

</font>

### <font size=2>step3: 安装 OpenClaw CLI</font>

<font size=2>

```bash
# 1. 重新安装 OpenClaw CLI
c

# 2. 修复 PATH
# 2.1 先查看 npm 全局安装位置
npm config get prefix

# 2.2 自动适配 prefix
echo 'export PATH="$(npm config get prefix)/bin:$PATH"' >> ~/.bashrc

# 3. 重启
source ~/.bashrc
hash -r

# 4. 验证
openclaw --version

# 5. 启动网关
openclaw gateway start
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

[user]
default=nights

[automount]
enabled=true
root=/mnt/
options=metadata,uid=1000,gid=1000,umask=0022,fmask=011,case=off

[interop]
enabled=true
appendWindowsPath=true
```

</font>

#### <font size=2>step2: 修改 openclaw.json 文件</font>

<font size=2>

> [!tip] 配置说明
> 以下为核心配置项说明,根据实际环境修改对应字段。

```json
{
  "agents": {
    "defaults": {
      "workspace": "/home/whites/.openclaw/workspace",
      "sandbox": {
        "mode": "off"                                 
      },
      "models": {
        "openrouter/auto": {
          "alias": "OpenRouter"
        },
        "openrouter/xiaomi/mimo-v2-pro": {}
      },
      "model": {
        "primary": "openrouter/xiaomi/mimo-v2-pro"
      }
    }
  },
  "gateway": {
    "mode": "local",
    "auth": {
      "mode": "token",
      "token": "your-token-here"
    },
    "port": 18789,
    "bind": "loopback",
    "tailscale": {
      "mode": "off",
      "resetOnExit": false
    },
    "controlUi": {
      "allowInsecureAuth": true
    },
    "nodes": {
      "denyCommands": [
        "camera.snap",
        "camera.clip",
        "screen.record",
        "contacts.add",
        "calendar.add",
        "reminders.add",
        "sms.send",
        "sms.search"
      ]
    }
  },
  "session": {
    "dmScope": "per-channel-peer"
  },
  "tools": {
    "profile": "full",
    "exec": {
      "host": "gateway",                    // 关键!必须改成 gateway 才能访问 K 盘
      "security": "full",                   // 完全权限
      "ask": "off"                          // 先关闭审批,测试成功后再改成 "on"
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
  },
  "auth": {
    "profiles": {
      "openrouter:default": {
        "provider": "openrouter",
        "mode": "api_key"
      }
    }
  },
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "your-app-id",
      "appSecret": "your-app-secret",
      "connectionMode": "websocket",
      "domain": "feishu",
      "groupPolicy": "open"
    }
  },
  "plugins": {
    "entries": {
      "xai": {
        "enabled": true,
        "config": {
          "webSearch": {
            "apiKey": "your-xai-api-key"
          }
        }
      },
      "feishu": {
        "enabled": true
      }
    }
  },
  "wizard": {
    "lastRunAt": "2026-04-02T09:39:39.148Z",
    "lastRunVersion": "2026.4.1",
    "lastRunCommand": "onboard",
    "lastRunMode": "local"
  },
  "meta": {
    "lastTouchedVersion": "2026.4.1",
    "lastTouchedAt": "2026-04-02T09:39:40.775Z"
  }
}
```

> [!caution] 安全提醒
> `token`、`appSecret`、`apiKey` 等敏感字段请替换为自己的值,不要直接使用示例中的占位符。

</font>




## <font size=3>安装辅助工具</font>

### <font size=2>ClawMetry</font>

<font size=2>

ClawMetry 是专为 OpenClaw 设计的开源实时监控面板。

```bash
# 安装
pipx install clawmetry

# 檢查 clawmetry 是否真的裝好
ls ~/.local/bin/clawmetry

# 把 ~/.local/bin 加到 PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 启动(自动打开 localhost:8900)
clawmetry
```

![step1](./images/openclaw-widnows-5.png)

区别于 `Windos + Docker Desktop + WSL + Ubuntu 本地部署.md` 的描述的配置方法, 由于不是在docker中进行的部署,执行 pip install clawmetry 会报错,Python 环境被系统标记为 externally-managed-environment(PEP 668 保护机制),不允许直接用 pip 修改系统 Python。

**通俗解释:** 从 Python 3.11 开始,系统自带的 Python(通过 apt install python3 安装的)被标记为 "由系统外部管理"。意思就是,操作系统(apt)才是这个 Python 的"主人",不允许直接用 pip install 随意安装或升级包。如果直接执行 pip install xxx,系统就会抛出这个错误:

```bash
error: externally-managed-environment
× This environment is externally managed
```

**解释原因:**
- 防止用 pip 安装的包和系统 apt 安装的包发生冲突(导致系统工具坏掉)
- 避免升级某个包时把系统自带的 Python 工具(比如 python3-pip、python3-apt 等)搞坏

</font>


---

### <font size=2>Karpathy LLM 知识库</font>

<font size=2>

Karpathy LLM Skill（也常称为 Karpathy LLM Wiki 或 Karpathy-style LLM Knowledge Base）并不是一个单一的软件包，而是一个模式（pattern） + 可安装的 Agent Skill。它的核心想法是：让 LLM（尤其是 Claude Code、Cursor、OpenClaw 等）自动把你的原始资料（文章、论文、图片等）编译成一个结构化的 Markdown Wiki（知识库），并持续维护、链接、更新它。人类只负责扔原始资料和提问，LLM 负责整理和合成知识。

这里我们运用他的核心思想来搭建自己的私人知识库，建议针对不同的领域，创建不同的 Vault.

```bash
# 这里假设我要创建 嵌入式 和 AI 两个领域的知识库，按照如下目录结构创建，如果要创建更多，则再新增子知识库即可

~/Knowledge-LLM-Wiki/                 ← 所有知识库的统一父目录（推荐）
├── embedded/                         ← 嵌入式系统知识库（独立一个 wiki）
│   ├── raw/                          ← 只放嵌入式相关的原始资料（文章、论文、芯片手册、代码等）
│   │   └── assets/                   ← 可选：存放图片、PDF附件等
│   └── wiki/                         ← LLM 只维护这个目录
│       ├── schema.md                 ← 嵌入式专用的规则文件
│       ├── index.md                  ← LLM 自动生成的总索引
│       ├── concepts/                 ← 概念页（如 rt-os.md、stm32.md）
│       ├── devices/                  ← 硬件设备页
│       ├── protocols/                ← 协议页
│       └── summaries/                ← 单个 raw 文件的总结页（可选）
│
└── ai/                               ← AI / LLM 知识库（另一个独立 wiki）
    ├── raw/                          ← 只放 AI 相关的原始资料
    │   └── assets/
    └── wiki/
        ├── schema.md                 ← AI 专用的规则文件
        ├── index.md
        ├── concepts/                 ← 如 transformer.md、agent.md
        ├── models/                   ← 模型相关页
        ├── techniques/               ← Prompt Engineering、RAG 等
        └── summaries/

```
接下来根据自己的需求，去完善目录中所需的文件内容。

**skill**

创建的这个本地知识库（~/Knowledge-LLM-Wiki/embedded/ 和 ~/Knowledge-LLM-Wiki/ai/）是纯 Markdown 文件，本身不是 Skill。
而 skills/ 文件夹（OpenClaw 的技能目录）的作用是存放 Agent Skill（让你的 Agent 知道如何使用、管理这些知识库的指令集）。


```bash
# 推荐结构如下（放在 OpenClaw 的 skills 目录下）：
~/.openclaw/workspace/skills/
├── llm-wiki-embedded/           ← 嵌入式知识库专用 Skill
│   ├── SKILL.md                 ← 核心文件（最重要）
│   └── README.md                ← 可选，说明
│
└── llm-wiki-ai/                 ← AI 知识库专用 Skill
    ├── SKILL.md
    └── README.md
```

</font>


---


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

**使用途径1**

在 openclaw.json 中添加如下字段配置，让 OpenClaw 能“看到”并使用 OpenSpace 的工具，并实现 Agent 的“自我进化”能力。

```bash
"mcp": {
  "servers": {
    "openspace": {
      "command": "openspace-mcp",
      "toolTimeout": 600,
      "env": {
        "OPENSPACE_HOST_SKILL_DIRS": "/home/whites/.openclaw/workspace/skills",
        "OPENSPACE_WORKSPACE": "/home/whites/OpenSpace"
      }
    }
  }
}
```

**使用途径2**

OpenSpace 提供了几个强大工具，例如：

- `execute_task`（执行复杂多步任务）
- `delegate-task`（任务委派）
- `skill-discovery`（技能发现与演化）


**启动后端(手动)**

```bash
openspace-dashboard --port 7788 --host 127.0.0.1

# 启动成功后会看到
Running on http://127.0.0.1:7788
```

**启动前端(手动)**

```bash
# 进入到这个路径
cd ~/OpenSpace/frontend

# 如果是第一次启动，需要安装依赖（只需执行一次）
npm install

# 启动前端开发服务器
npm run dev -- --host 127.0.0.1 --port 3789
```

**启动前后端(自动)**

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
  # 确保依赖已安装
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



### <font size=2>Osidian</font>

<font size=2>



</font>