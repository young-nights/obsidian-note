---
tags: [config, guide]
created: 2026-04-02 18:19:00
---

# <font size=4>Windows + WSL + Ubuntu + OpenClaw 本地部署</font>

## <font size=3>简要概述</font>

<font size=2>

> [!info] 部署思路
> OpenClaw 的核心卖点就是"能够操作电脑文件、跑命令、整理资料"，所以它设计上就是要访问文件的。但是如果让 OpenClaw 直接部署在宿主机（使用者常用的 Windows 环境）中，存在很高的安全风险，因此需要通过 WSL 进行隔离部署。

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

# 3.2 卸载（删除）指定发行版
wsl --unregister Ubuntu-22.04

# 4. 查看可用的 Ubuntu 版本
wsl --list --online

# 4.1 安装特定版本（例如 Ubuntu 22.04）
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
# 推荐安装方式：一键脚本
curl -fsSL https://openclaw.ai/install.sh | bash
```

</font>

### <font size=2>step3: 安装 OpenClaw CLI</font>

<font size=2>

```bash
# 1. 重新安装 OpenClaw CLI
npm install -g openclaw@latest

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
> 以下为核心配置项说明，根据实际环境修改对应字段。

```json
{
  "agents": {
    "defaults": {
      "workspace": "/home/whites/.openclaw/workspace",
      "sandbox": {
        "mode": "off"                                   // 关键！必须改成 gateway 才能访问 K 盘
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
      "host": "gateway",                    // 关键！必须改成 gateway 才能访问 K 盘
      "security": "full",                   // 完全权限
      "ask": "off"                          // 先关闭审批，测试成功后再改成 "on"
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
> `token`、`appSecret`、`apiKey` 等敏感字段请替换为自己的值，不要直接使用示例中的占位符。

</font>
