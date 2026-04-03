---
tags:
  - openclaw
created: 2026-04-02 18:19:00
---

# <font size=4>Ubuntu Desktop 20.04.2 部署OpenClaw</font>

## <font size=3>前置准备</font>

<font size=2>

```bash

# 1. 更新安装工具
sudo apt update && sudo apt upgrade -y

# 2. 安装 curl、git 等基础工具
sudo apt install curl git build-essential -y

# 3. 安装 curl 工具
sudo apt install curl

# 4. 安装 Node.js (OpenClaw 依赖 Node.js ≥22)
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# 5. 验证
node --version   # 应该显示 v22.x 或更高
npm --version

```

</font>

## <font size=3>一键安装</font>

<font size=2>


```bash
# 推荐安装方式：一键脚本
curl -fsSL https://openclaw.ai/install.sh | bash
```

</font>

## <font size=3>使用方法</font>

<font size=2>

```bash
# 1. 部署完成以后可以验证一下 openclaw 的状态
openclaw gateway status

# 1.1 如果没开启可以重启
openclaw gateway restart

# 2. 如果需要配置，打开 onboard 面板
openclaw onboard

# 3. 重新打開 OpenClaw 的網站
openclaw dashboard
```

</font>
