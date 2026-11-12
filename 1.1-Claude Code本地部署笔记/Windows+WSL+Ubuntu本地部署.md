---
tags:
  - openclaw
  - claude-code
  - deepseek
created: 2026-05-09 07:36:00
updated: 2026-11-12
---

# Windows + WSL + Ubuntu 环境下的 Claude Code 部署与配置

> [!info] 版本说明
> 本文档基于 **@anthropic-ai/claude-code 2.1.322** 编写，适用于 Windows 11 + WSL2 (Ubuntu) 环境。
> 当前部署方案：**DeepSeek API**（Anthropic 兼容协议）作为后端，免登录直接使用。
> 安装前请确认版本：`claude --version`

## 简要概述

> [!info] Claude Code 是什么
> Claude Code 是 Anthropic 官方发布的终端编程智能体（coding agent），支持交互式会话和非交互式管道模式。
> 核心优势：直接操作文件系统、执行 shell 命令、集成 Git 工作流，是当前最强的 AI 编程助手之一。
>
> Claude Code 通过 `ANTHROPIC_BASE_URL` 支持任意 Anthropic 兼容协议的后端：
> 1. **官方 Anthropic API**（`api.anthropic.com`）：需要 Anthropic API Key
> 2. **DeepSeek API**（`api.deepseek.com/anthropic`）：DeepSeek 官方 Anthropic 兼容端点，`claude-*` 模型名自动映射到 DeepSeek 模型（**本文档当前方案**）
> 3. **其他自定义代理**：如小米 Token Plan 等 Anthropic 兼容服务

**架构概览（当前部署）**

```
Windows 11 宿主机
  └── WSL2 (Ubuntu)
        ├── Claude Code (2.1.322)
        │     ├── 认证: ANTHROPIC_AUTH_TOKEN (DeepSeek API Key，免登录)
        │     ├── 连接: api.deepseek.com/anthropic
        │     ├── 默认模型: deepseek-flash[1m]
        │     └── /model 可选: DeepSeek-Flash / DeepSeek-V4-Pro
        └── (可选) OpenClaw Gateway / OpenSpace MCP —— 参见 Openclaw 笔记
```

## 前置条件

> [!caution] 必需项
> - **Claude Code 安装方式**二选一：
>   - npm 全局安装：需要 **Node.js ≥ 22**（参考 [../1.2-Openclaw 本地部署笔记/Windows+WSL+Ubuntu本地部署.md](../1.2-Openclaw%20本地部署笔记/Windows+WSL+Ubuntu本地部署.md) step1，若 OpenClaw 已装则自带）
>   - 官方安装脚本（native 模式）：**不需要 Node**，安装于 `~/.local/share/claude/`
> - **DeepSeek API Key**（当前方案）：在 [platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys) 申请，以 `sk-` 开头
>   - 也可用官方 Anthropic Key 或其他兼容服务 Token，见 step2 的方式 B / C

## 安装 Claude Code

### step1: 安装

```bash
# 方式一：npm 全局安装（需要 Node.js）
npm install -g @anthropic-ai/claude-code

# 方式二：如果已通过官方安装脚本安装（native 模式），跳过上面命令
# 确认安装位置
which claude
# native 安装通常为: ~/.local/bin/claude → ~/.local/share/claude/versions/<版本>

# 验证安装
claude --version
# 预期输出: 2.1.x (Claude Code)
```

> [!tip] 如果 openclaw 已安装
> Claude Code 通常随 OpenClaw 一起安装，无需重复执行。可通过 `which claude` 确认是否已存在。

### step2: 配置 API 提供商

配置文件为 `~/.claude/settings.json`，三种后端任选其一。

#### 方式 A：DeepSeek（当前部署方案）

```bash
mkdir -p ~/.claude
```

创建/修改 `~/.claude/settings.json`（`<你的 DeepSeek API Key>` 替换为真实 key）：

```json
{
  "theme": "dark",
  "model": "deepseek-flash[1m]",
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "<你的 DeepSeek API Key>",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "deepseek-v4-pro[1m]",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "deepseek-flash[1m]",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "deepseek-flash",
    "CLAUDE_CODE_SUBAGENT_MODEL": "deepseek-flash",
    "CLAUDE_CODE_EFFORT_LEVEL": "max",
    "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "786432"
  },
  "modelPicker": {
    "replaceBuiltInOptions": true,
    "options": [
      {
        "model": "deepseek-flash[1m]",
        "label": "DeepSeek-Flash",
        "description": "Latest flagship agentic coding model, supports image input (1M context)",
        "behavesAs": "claude-sonnet-5-5"
      },
      {
        "model": "deepseek-v4-pro[1m]",
        "label": "DeepSeek-V4-Pro",
        "description": "Most capable flagship agentic coding model (1M context)",
        "behavesAs": "claude-opus-5-5"
      }
    ]
  }
}
```

> [!tip] 字段说明
>
> | 字段 | 说明 |
> |------|------|
> | `model` | 会话默认模型。**推荐用这个字段**而不是 env 的 `ANTHROPIC_MODEL`（原因见下方 warning） |
> | `env.ANTHROPIC_BASE_URL` | DeepSeek 的 Anthropic 兼容端点，固定为 `https://api.deepseek.com/anthropic` |
> | `env.ANTHROPIC_AUTH_TOKEN` | DeepSeek API Key（Bearer 认证；官方 API 则用 `ANTHROPIC_API_KEY`，二选一） |
> | `env.ANTHROPIC_DEFAULT_OPUS_MODEL` | 模型别名 `opus` / `opusplan` 实际调用的模型 |
> | `env.ANTHROPIC_DEFAULT_SONNET_MODEL` | 模型别名 `sonnet` 实际调用的模型 |
> | `env.ANTHROPIC_DEFAULT_HAIKU_MODEL` | 模型别名 `haiku` / 后台任务实际调用的模型 |
> | `env.CLAUDE_CODE_SUBAGENT_MODEL` | 子代理（subagent）默认模型 |
> | `env.CLAUDE_CODE_EFFORT_LEVEL` | 默认推理深度（low/medium/high/max），DeepSeek 官方推荐 `max` |
> | `env.CLAUDE_CODE_AUTO_COMPACT_WINDOW` | 自动压缩触发阈值（token 数），DeepSeek 官方推荐 `786432` |
> | `modelPicker` | 自定义 `/model` 列表，让选择器直接显示 DeepSeek 模型（详见下文） |

> [!warning] 为什么不设置 env 的 `ANTHROPIC_MODEL`
> `ANTHROPIC_MODEL` 环境变量的优先级高于 settings 的 `model` 字段，**每次启动都会强制生效**，导致你在 `/model` 里选的模型重启后被覆盖回去。
> 手动部署推荐：默认模型写进 settings 顶层 `model` 字段，env 里只放地址、key 和别名映射。

**DeepSeek 模型速查**

| 模型名 | 定位 | 上下文 | 备注 |
|--------|------|--------|------|
| `deepseek-flash` | 旗舰编程模型，速度快 | 1M | 支持图片输入；日常默认 |
| `deepseek-v4-pro` | 最强旗舰编程模型 | 1M | 纯文本；复杂任务 |

- **`[1m]` 后缀**是 Claude Code 的上下文窗口标记（1M tokens），会从请求模型名中剥离，DeepSeek 官方文档也使用该写法。
- **`behavesAs`**（可选，需 v2.1.257+）：填一个你版本已知的模型 ID（如 `claude-sonnet-5-5`），让 Claude Code 按该模型的能力/推理档位处理自定义模型，避免 `unrecognized_model` 告警。请求中发送的模型 ID 不变。
- **`modelPicker.replaceBuiltInOptions: true`**：`/model` 只显示上面配置的行 + Default + 当前模型；不加这个字段则追加在内置 Opus/Sonnet/Haiku 行之后。
- **别名兜底**：即使直接指定 `claude-*` 模型名，DeepSeek 也会自动映射（`claude-opus*` → `deepseek-v4-pro`，`claude-sonnet*`/`claude-haiku*` → `deepseek-flash`）。
- **联网搜索**：DeepSeek 后端原生支持 Claude Code 的 Web Search 工具，模型认为需要时自动触发；搜索/抓取按次计费（[Search 计费](https://api-docs.deepseek.com/guides/search.md#billing)），另产生一次总结用的 LLM token 费用。

#### 方式 B：使用官方 Anthropic API

```json
{
  "env": {
    "ANTHROPIC_API_KEY": "sk-ant-your-key-here"
  }
}
```

#### 方式 C：其他 Anthropic 兼容代理（如小米 Token Plan）

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://token-plan-cn.xiaomimimo.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "tp-your-token-here",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "mimo-v2-pro",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "mimo-v2-pro",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "mimo-v2-flash"
  }
}
```

> [!caution] 安全提醒
> - `settings.json` 包含认证信息，确保文件权限：`chmod 600 ~/.claude/settings.json`
> - 不要将此文件提交到 Git 仓库，笔记/截图中也不要粘贴真实 key
> - `ANTHROPIC_AUTH_TOKEN` 和 `ANTHROPIC_API_KEY` 二选一，不要同时配置

### step3: 跳过登录页，直接进入工作环境

配置 API key 后，还需在全局配置 `~/.claude.json` 里标记引导完成、预授权 API key，否则首次启动会进入登录/引导流程：

```bash
python3 - <<'EOF'
import json
p = '/home/nights/.claude.json'   # WSL 下即 ~/.claude.json
cfg = json.load(open(p))
key = "<你的 DeepSeek API Key>"

cfg['hasCompletedOnboarding'] = True                       # 跳过首次引导
resp = cfg.setdefault('customApiKeyResponses', {'approved': [], 'rejected': []})
if key not in resp['approved']:                            # 免每次询问"是否使用此 API key"
    resp['approved'].append(key)
resp['rejected'] = [k for k in resp.get('rejected', []) if k != key]

json.dump(cfg, open(p, 'w'), indent=2)
print('done:', cfg['hasCompletedOnboarding'], [k[:5]+'...' for k in resp['approved']])
EOF
```

两个字段的作用：

| 文件 | 字段 | 作用 |
|------|------|------|
| `~/.claude.json` | `hasCompletedOnboarding: true` | 跳过主题选择/登录引导，直接进入工作环境 |
| `~/.claude.json` | `customApiKeyResponses.approved: ["<key>"]` | 预授权 API key，免去每次启动的"是否使用此 API key？"询问 |

> [!tip] 目录信任弹窗（正常现象）
> 首次在**每个新目录**启动 `claude` 会弹出一次「是否信任此文件夹」的安全确认，选 **Yes, I trust this folder** 即可。
> 这是 Claude Code 的目录沙箱机制（决定能否读写/执行该目录的文件），不是登录页，每个目录只需确认一次，结果记录在 `~/.claude.json` 的 `projects.<路径>.hasTrustDialogAccepted`。

### step4: 验证部署

```bash
# 1. 版本检查
claude --version

# 2. 非交互式连通性测试（走真实 API，消耗少量 token）
claude -p "Reply with exactly: PONG"
# 预期输出: PONG

# 3. JSON 配置格式校验（改错配置后必查）
python3 -m json.tool ~/.claude/settings.json > /dev/null && echo OK
python3 -m json.tool ~/.claude.json > /dev/null && echo OK
```

交互式验证：

```bash
cd /path/to/project
claude
```

预期表现：
1. 启动横幅显示 `DeepSeek-Flash · API Usage Billing`（模型名 + API 计费模式），**没有登录页**
2. 输入 `/model`，列表显示 `DeepSeek-Flash` / `DeepSeek-V4-Pro` 两个条目
3. 随便发一句话，模型正常回复

## /model 模型列表配置（modelPicker）

`modelPicker` 让 `/model` 选择器按自己的顺序和标签显示模型，对自定义后端尤其重要——否则列表里只有 Anthropic 内置模型行。

```json
{
  "modelPicker": {
    "replaceBuiltInOptions": true,
    "options": [
      { "model": "deepseek-flash[1m]", "label": "DeepSeek-Flash", "description": "...", "behavesAs": "claude-sonnet-5-5" },
      { "model": "deepseek-v4-pro[1m]", "label": "DeepSeek-V4-Pro", "description": "...", "behavesAs": "claude-opus-5-5" }
    ]
  }
}
```

| 字段 | 说明 |
|------|------|
| `options[].model` | 发给 API 的模型 ID（`[1m]` 后缀可加可不加） |
| `options[].label` | 选择器里显示的名字 |
| `options[].description` | 第二行描述文字 |
| `options[].behavesAs` | 可选，借用已知模型的能力描述（v2.1.257+） |
| `replaceBuiltInOptions` | `true` = 只显示这些行 + Default + 当前模型；`false`/缺省 = 追加在内置行之后 |

选择器操作：**Enter** = 切换并保存为新会话默认值（写入 settings 的 `model` 字段）；**s** = 仅本会话生效；**Esc** = 取消。

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

启动交互式会话后，可使用以下斜杠命令（完整清单见 [Claude Code 使用说明](./Claude%20Code%20使用说明.md)）：

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
| `/doctor` | 诊断安装和运行问题 |

### 与 OpenClaw 集成（ACP 模式）

Claude Code 可作为 OpenClaw 的 ACP（Agent Coding Partner）子代理使用：

```bash
# 在 OpenClaw 中 spawn 一个 Claude Code 会话
# 通过 sessions_spawn 使用 runtime="acp"
```

> [!info] ACP 集成
> OpenClaw 支持通过 `sessions_spawn(runtime="acp", agentId="claude-code")` 调用 Claude Code。
> 配置方式参考 [../1.2-Openclaw 本地部署笔记/Windows+WSL+Ubuntu本地部署.md](../1.2-Openclaw%20本地部署笔记/Windows+WSL+Ubuntu本地部署.md) 的 ACP 配置章节。

## 模型切换

### 交互式切换

```
/model                    # 打开选择器（DeepSeek 部署下显示 DeepSeek-Flash / DeepSeek-V4-Pro）
/model deepseek-v4-pro    # 直接指定模型 ID
```

### 通过配置切换

修改 `~/.claude/settings.json` 顶层 `model` 字段：

```json
{
  "model": "deepseek-v4-pro[1m]"
}
```

> [!tip] DeepSeek 双模型使用建议
> - **DeepSeek-Flash**（`deepseek-flash`）：速度快、支持图片，适合日常编码
> - **DeepSeek-V4-Pro**（`deepseek-v4-pro`）：最强推理，适合复杂架构决策、疑难 bug
> - 别名兜底：`/model opus` → 实际走 `deepseek-v4-pro`，`/model sonnet` → 实际走 `deepseek-flash`（由 `ANTHROPIC_DEFAULT_*_MODEL` 映射）

## 安全与权限

### 权限模式

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| 默认 | 每次工具调用需确认 | 生产环境，安全第一 |
| auto | 自动判断信任操作（2.1.x 默认） | 日常使用 |
| `--dangerously-skip-permissions` | 跳过所有权限检查 | 沙箱/离线环境 |
| `--allow-dangerously-skip-permissions` | 允许但不默认启用 | 按需使用 |

快捷键 `Shift+Tab` 循环切换权限模式。

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

**原因**：API Key 无效或未配置。

**解决**：
1. 确认 `~/.claude/settings.json` 存在且格式正确
2. 检查 `ANTHROPIC_AUTH_TOKEN` 是否为有效 key（DeepSeek key 以 `sk-` 开头）
3. 如使用官方 API，检查 `ANTHROPIC_API_KEY` 是否正确
4. 确认 key 未被删除/停用：`curl -s https://api.deepseek.com/models -H "Authorization: Bearer $KEY"`

### Q2: 启动时出现登录页 / 每次询问 API key

**原因**：`~/.claude.json` 缺少跳过登录的标记。

**解决**：执行 step3，写入 `hasCompletedOnboarding: true` 并把 key 加进 `customApiKeyResponses.approved`。

> [!note] 目录信任弹窗 ≠ 登录页
> 每个新目录第一次启动时的「是否信任此文件夹」是安全机制，无法也不应全局跳过，确认一次即记住。

### Q3: `/model` 列表里没有 DeepSeek 模型

**原因**：`modelPicker` 未配置或格式错误，选择器回退到内置 Anthropic 模型行。

**解决**：
1. 对照 step2 方式 A 检查 `modelPicker` 字段（必须在 `~/.claude/settings.json` 用户级配置，项目级 `.claude/settings.json` 会被忽略）
2. 校验 JSON：`python3 -m json.tool ~/.claude/settings.json`
3. 重启 claude 后再输入 `/model` 查看

### Q4: 出现 `[claude-code:unrecognized_model]` 提示

**原因**：Claude Code 内置模型目录不包含 `deepseek-*` 这类自定义模型 ID，属正常提示，**不影响使用**（请求照常发送到 DeepSeek）。

**解决**：在 `modelPicker` 行上加 `behavesAs`（借用已知模型的能力描述），或忽略该提示。

### Q5: 连接超时

```text
Error: connect ETIMEDOUT
```

**原因**：无法连接到 `ANTHROPIC_BASE_URL` 指定的地址。

**解决**：
1. 检查网络连通性：`curl -sI https://api.deepseek.com/anthropic`
2. 检查 WSL 的 DNS 配置：`cat /etc/resolv.conf`
3. 如在中国大陆访问官方 Anthropic API 受限，优先使用 DeepSeek 等国内兼容端点

### Q6: settings.json 格式错误

```text
Error: Unexpected token in JSON
```

**原因**：JSON 格式有误（常见于多余逗号）。

**解决**：
```bash
python3 -m json.tool ~/.claude/settings.json
```

### Q7: 配置文件位置

| 文件 | 路径 | 用途 |
|------|------|------|
| settings.json | `~/.claude/settings.json` | API 配置 + 环境变量 + 模型默认值 + modelPicker |
| 全局配置 | `~/.claude.json` | 引导状态、API key 授权、目录信任记录、会话统计 |
| 会话数据 | `~/.claude/sessions/` | 历史会话 |
| 项目配置 | `<项目>/.claude/settings.json` | 项目级设置（**不支持 modelPicker / provider 配置**） |

## 运维命令

```bash
# 查看版本
claude --version

# 更新
claude update
# 或 npm 方式: npm update -g @anthropic-ai/claude-code

# 查看配置
cat ~/.claude/settings.json

# 调试模式（排查连接问题）
claude -d "test connection"

# 诊断安装/配置问题（会话内也可用 /doctor）
claude doctor

# 清除会话历史
rm ~/.claude/sessions/*
```

---

## 变更记录

| 版本 | 日期 | 主要改动 |
|------|------|---------|
| 1.0 | 2026-05-09 | 初始版本，基于 @anthropic-ai/claude-code 2.1.109，小米 Token Plan 代理 + mimo 模型 |
| 2.0 | 2026-11-12 | 按实际部署更新：升级到 2.1.322；后端切换为 DeepSeek（`api.deepseek.com/anthropic`）；新增 modelPicker 自定义 `/model` 列表、`[1m]` 上下文标记、`behavesAs` 说明；新增 step3 跳过登录页（`hasCompletedOnboarding` / `customApiKeyResponses`）与目录信任弹窗说明；更正 `ANTHROPIC_MODEL` env 覆盖 `/model` 选择的问题（改用 settings `model` 字段）；补充部署验证步骤与新 FAQ；保留官方 API / 小米代理作为备选方案 |
