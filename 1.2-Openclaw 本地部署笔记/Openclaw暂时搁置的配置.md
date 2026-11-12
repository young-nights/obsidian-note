---
tags:
  - openclaw
  - 搁置
created: 2026-04-30 06:41:00
---

# OpenClaw 暂时搁置的配置

> [!info] 说明
> 记录已发现但暂时不处理的配置项，待条件成熟时继续完成。

---

## Codex CLI + ACP 集成

### 状态：❌ 搁置（缺少 OpenAI API Key）

**发现日期**: 2026-04-30

### 已完成的部分

| 组件 | 状态 | 版本/详情 |
|------|------|----------|
| Codex CLI | ✅ 已安装 | v0.125.0，`codex --version` 正常 |
| codex-acp 适配器 | ✅ 已安装 | @zed-industries/codex-acp@0.11.1 |
| ACPX Runtime 插件 | ✅ 已加载 | OpenClaw 内置，2026.4.22 |
| Codex 插件 | ✅ 已加载 | OpenClaw 内置，2026.4.22 |
| Vendor 二进制 | ✅ 正常 | codex exec 可启动 |

### 待完成的部分

| 组件 | 状态 | 说明 |
|------|------|------|
| OpenAI API Key | ❌ 未提供 | Codex 必须使用 OpenAI 官方 API，不兼容小米/OpenRouter |
| ~/.codex/config.toml | ❌ 未创建 | 需要 API Key 后创建 |
| OPENAI_API_KEY 环境变量 | ❌ 未设置 | 需要 API Key 后设置 |
| Bubblewrap | ⚠️ 未安装 | `sudo apt install bubblewrap`，sandbox 执行依赖 |
| ACP 配置 (openclaw.json) | ❌ 未配置 | 需要在 plugins.entries 或 acp 段中配置 |

### 关键发现：Codex 不兼容小米/OpenRouter

Codex 使用的是 OpenAI **Responses API**（WebSocket 协议，端点 `/v1/responses`），而非标准的 Chat Completions API。

```
Codex → wss://api.xiaomimimo.com/v1/responses → 404 Not Found
Codex → wss://openrouter.ai/api/v1/responses   → 404 Not Found
Codex → wss://api.openai.com/v1/responses       → ✅ 正常（需 API Key）
```

**结论**: Codex 只能使用 OpenAI 官方 API，无法使用小米 MiMo 或 OpenRouter 路由的模型。

### 后续恢复步骤

当准备好 OpenAI API Key 时，按以下步骤完成配置：

**1. 创建 Codex 配置文件**

```bash
cat > ~/.codex/config.toml << 'EOF'
model = "o4-mini"
approval_policy = "on-request"
sandbox_mode = "read-only"
EOF
```

**2. 设置 API Key**

```bash
# 方式一：环境变量（推荐）
echo 'export OPENAI_API_KEY="sk-xxxx..."' >> ~/.bashrc
source ~/.bashrc

# 方式二：通过 codex login
echo "$OPENAI_API_KEY" | codex login --with-api-key
```

**3. 安装 bubblewrap（可选，启用 sandbox）**

```bash
sudo apt install bubblewrap
```

**4. 在 openclaw.json 中配置 ACP**

```jsonc
{
  "acp": {
    "allowedAgents": ["codex", "claude"],
    "defaultAgent": "codex"
  }
}
```

**5. 验证**

```bash
# 直接测试
codex exec "hello, respond with just 'hi'"

# 通过 OpenClaw ACP 测试
openclaw acp doctor
```

**6. 更新部署文档**

将配置过程写入 `Windows+WSL+Ubuntu本地部署.md` 的辅助工具章节。

---
