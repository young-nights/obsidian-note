---
title: Claude Code 使用说明
type: tutorial
tags: [claude-code, cli, productivity, ai-coding]
created: 2026-05-10
updated: 2026-05-10
---

# Claude Code 使用说明

> Anthropic 官方终端 AI 编程工具，支持 CLI 交互、文件编辑、Shell 执行、子代理、MCP 扩展等。

## 1. 启动与会话管理

| 命令 | 用途 | 示例 |
|------|------|------|
| `claude` | 启动交互式会话 | `claude` |
| `claude "query"` | 启动并带初始提示 | `claude "explain this project"` |
| `claude -p "query"` | 单次查询后退出 | `claude -p "explain this function"` |
| `cat file \| claude -p` | 处理管道输入 | `cat logs.txt \| claude -p "explain"` |
| `claude -c` | 继续最近一次对话 | `claude -c` |
| `claude -c -p "query"` | 继续对话并单次查询 | `claude -c -p "Check for type errors"` |
| `claude -r "<session>" "query"` | 恢复指定会话 | `claude -r "auth-refactor" "Finish this PR"` |
| `claude update` | 更新到最新版 | `claude update` |

---

## 2. 斜杠命令（Slash Commands）

在会话中输入 `/` 开头的命令。以下按工作流阶段分类。

### 2.1 项目初始化

| 命令 | 用途 | 何时使用 |
|------|------|----------|
| `/init` | 生成项目级 `CLAUDE.md` 模板 | 首次在新仓库使用 Claude Code 时 |
| `/memory` | 编辑 `CLAUDE.md` 项目记忆文件 | 需要修改项目规范、约定、常用命令时 |
| `/mcp` | 配置 MCP 服务器 | 需要连接外部工具（数据库、API、Slack 等） |
| `/agents` | 管理子代理配置（创建/编辑/删除） | 需要创建专用子代理或查看已有代理时 |
| `/permissions` | 设置审批规则 | 需要控制哪些操作自动通过、哪些需要确认时 |

### 2.2 编码与任务执行

| 命令 | 用途 | 何时使用 |
|------|------|----------|
| `/add-dir <path>` | 添加额外工作目录 | 项目依赖另一个仓库/目录的代码，需要 Claude 读取或编辑时 |
| `/plan` | 切换到计划模式 | 大范围修改前，让 Claude 先分析再动手 |
| `/model` | 切换模型 | 需要更强推理（Opus）或更快响应（Haiku）时 |
| `/effort` | 调整推理深度 | 简单任务用低推理节省 token，复杂问题用高推理 |
| `/compact` | 压缩对话上下文 | 对话太长，token 占用过多时 |
| `/context` | 查看上下文使用情况 | 想知道 token 消耗在哪里时 |
| `/btw <question>` | 快速旁问 | 问一个不相关的小问题，不污染主对话历史 |

### 2.3 代码审查与提交

| 命令 | 用途 | 何时使用 |
|------|------|----------|
| `/diff` | 查看当前变更 | 修改后想确认改了什么 |
| `/simplify` | 审查并简化最近修改的代码 | 代码写完后，自动优化质量、去除冗余 |
| `/review` | 深度代码审查 | 需要只读审查意见（不修改代码） |
| `/security-review` | 安全审查 | 关注潜在安全漏洞 |
| `/autofix-pr [prompt]` | 自动修复 PR 问题 | PR 的 CI 失败或 reviewer 评论需要自动修复 |

### 2.4 会话管理

| 命令 | 用途 | 何时使用 |
|------|------|----------|
| `/clear` | 清空对话开始新任务 | 当前任务完成，开始新任务时 |
| `/resume` | 恢复之前的对话 | 想回到之前的某次对话继续 |
| `/branch` 或 `/fork` | 创建对话分支 | 想在当前节点尝试不同方案，保留原对话 |
| `/rewind` | 回滚代码和对话到检查点 | 发现方向错了，需要撤销 |
| `/compact` | 压缩上下文 | 对话太长占用太多 context window |

### 2.5 诊断与调试

| 命令 | 用途 | 何时使用 |
|------|------|----------|
| `/doctor` | 诊断安装和运行问题 | Claude Code 行为异常时 |
| `/debug` | 调试运行时问题 | 需要排查具体错误 |
| `/feedback` | 提交 bug 反馈 | 发现 bug 并附带会话上下文 |

### 2.6 内置技能（Bundled Skills）

| 命令 | 用途 | 何时使用 |
|------|------|----------|
| `/simplify` | 代码简化优化 | 代码写完后自动应用质量和效率改进 |
| `/batch <instruction>` | 并行大规模重构 | 需要跨代码库做大量同类修改（如迁移框架） |
| `/debug` | 系统性调试 | 遇到 bug 需要系统性排查 |
| `/loop` | 循环迭代任务 | 需要反复执行直到满足条件 |
| `/claude-api` | Claude API 参考 | 项目使用 Anthropic SDK 时自动加载 |

---

## 3. 重点命令详解

### 3.1 `/add-dir` — 添加工作目录

**用途**：让 Claude Code 访问当前项目目录之外的文件。

**什么时候需要**：
- 你的代码引用了另一个仓库的库
- 需要读取或编辑 `../` 父目录下的文件
- Monorepo 中多个 package 在不同目录

**用法**：
```
/add-dir ../apps ../lib
```

**注意**：
- 只授予文件访问权限，不会加载该目录的 `.claude/` 配置
- 该目录下的 `.claude/skills/` 会自动加载（是例外）
- `CLAUDE.md` 默认不加载，需设置 `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`
- 持久化：在 settings 中设置 `permissions.additionalDirectories`

---

### 3.2 `/agents` — 管理子代理

**用途**：创建和管理专用 AI 子代理，每个子代理有独立上下文、系统提示、工具权限。

**什么时候需要**：
- 反复执行同类任务（如代码审查、测试生成、部署）
- 想把搜索/探索任务隔离到独立上下文，节省主对话 token
- 需要限制某个任务的工具权限（如只读审查）

**内置子代理**：

| 子代理 | 模型 | 用途 |
|--------|------|------|
| Explore | Haiku（快速） | 只读代码搜索和分析 |
| Plan | 继承主对话 | 计划模式中的代码库研究 |
| General-purpose | 继承主对话 | 复杂多步骤任务 |

**用法**：
```
/agents                    # 打开管理界面
claude agents              # CLI 列出所有已配置子代理
```

**自定义子代理存放位置**：

| 位置 | 范围 | 路径 |
|------|------|------|
| 个人级 | 所有项目可用 | `~/.claude/agents/` |
| 项目级 | 仅当前项目 | `.claude/agents/` |

**示例**：创建一个代码审查子代理
```markdown
---
name: code-reviewer
description: Review code changes for quality, bugs, and best practices
model: sonnet
tools: Read, Grep, Glob
---

Review the provided code for:
1. Bugs and logic errors
2. Performance issues
3. Code style violations
4. Missing error handling
```

---

### 3.3 `/init` — 初始化项目

**用途**：在当前仓库生成 `CLAUDE.md`，包含项目结构、约定、常用命令等。

**什么时候用**：首次在新仓库使用 Claude Code 时。

**生成内容**：
- 项目概述和目录结构
- 构建/测试/部署命令
- 代码风格约定
- 常用工作流

---

### 3.4 `/plan` — 计划模式

**用途**：让 Claude 先分析和规划，确认后再执行。

**什么时候用**：
- 大范围重构（修改多个文件）
- 不确定最佳方案，需要 Claude 先出方案
- 需要预览改动范围

**工作流程**：
```
/plan 帮我重构这个模块的错误处理逻辑
→ Claude 分析代码库，输出修改计划
→ 你确认/修改计划
→ Claude 按计划执行
```

---

### 3.5 `/compact` — 压缩上下文

**用途**：将长对话压缩为摘要，释放 context window。

**什么时候用**：
- 对话超过 20+ 轮，token 消耗明显变大
- 想继续同一任务但减少历史占用

**注意**：
- 压缩后丢失细节，只保留摘要
- `CLAUDE.md` 和技能内容不受影响
- 可选传入聚焦指令：`/compact focus on the API refactor`

---

### 3.6 `/btw` — 旁问

**用途**：问一个与当前任务无关的小问题，不会添加到对话历史。

**什么时候用**：
- 正在写代码，突然想问"这个 Python 装饰器怎么用"
- 不想打断主任务流

**用法**：
```
/btw Python 的 @dataclass 和 NamedTuple 有什么区别
```

---

### 3.7 `/rewind` — 回滚

**用途**：将代码和/或对话恢复到之前的检查点。

**什么时候用**：
- Claude 的修改方向不对，需要撤销
- 想回到之前的某个节点重试

**用法**：
```
/rewind                    # 弹出检查点选择
Esc Esc                    # 快捷键触发
```

---

### 3.8 `/batch` — 并行大规模修改

**用途**：将大型重构任务分解为多个独立单元，每个在独立 git worktree 中并行执行。

**什么时候用**：
- 框架迁移（如 React → Solid）
- 大量文件的同类修改（如统一 API 格式）
- 批量添加类型注解

**用法**：
```
/batch migrate src/ from JavaScript to TypeScript
```

**要求**：需要 git 仓库。每个工作单元在独立 worktree 中执行，互不干扰。

---

## 4. 自定义技能（Skills）

技能是 `SKILL.md` 文件，放在特定目录下，Claude Code 自动发现并使用。

### 存放位置

| 级别 | 路径 | 范围 |
|------|------|------|
| 个人 | `~/.claude/skills/<skill-name>/SKILL.md` | 所有项目 |
| 项目 | `.claude/skills/<skill-name>/SKILL.md` | 当前项目 |
| 插件 | `<plugin>/skills/<skill-name>/SKILL.md` | 插件启用范围 |

### 用法
```
/my-skill                  # 直接调用
"帮我做 xxx"              # Claude 根据 description 自动选择
```

### 示例：创建技能
```bash
mkdir -p ~/.claude/skills/summarize-changes
```

```yaml
# ~/.claude/skills/summarize-changes/SKILL.md
---
description: Summarizes uncommitted changes and flags anything risky
---

## Current changes
!`git diff HEAD`

## Instructions
Summarize changes in bullet points, then list risks.
```

---

## 5. 快捷键速查

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+C` | 取消当前输入/生成 |
| `Ctrl+D` | 退出会话 |
| `Ctrl+L` | 重绘屏幕 |
| `Ctrl+O` | 切换转录查看器（详细工具调用记录） |
| `Ctrl+T` | 切换任务列表 |
| `Ctrl+R` | 反向搜索命令历史 |
| `Ctrl+G` | 在外部编辑器中编辑提示 |
| `Esc Esc` | 回滚或摘要 |
| `Shift+Tab` | 循环权限模式 |
| `Option+P` | 切换模型 |
| `Option+T` | 切换扩展推理 |
| `Option+O` | 切换快速模式 |
| `Shift+Enter` | 多行输入 |
| `!` 开头 | Shell 模式（直接执行命令） |
| `@` | 文件路径自动补全 |

---

## 6. CLI 标志

| 标志 | 用途 | 示例 |
|------|------|------|
| `--add-dir` | 添加工作目录 | `claude --add-dir ../apps ../lib` |
| `--agent` | 指定子代理 | `claude --agent code-reviewer` |
| `--model` | 指定模型 | `claude --model claude-sonnet-4-20250514` |
| `-p` | 单次查询模式 | `claude -p "fix the bug"` |
| `-c` | 继续最近对话 | `claude -c` |
| `-r` | 恢复指定会话 | `claude -r "session-name" "continue"` |
| `--permission-mode` | 设置权限模式 | `claude --permission-mode auto` |

---

## 7. 权限模式

| 模式 | 行为 |
|------|------|
| `default` | 每个操作需确认 |
| `acceptEdits` | 文件编辑自动通过 |
| `plan` | 只分析不执行 |
| `auto` | 自动判断信任操作 |
| `bypassPermissions` | 跳过所有确认（危险） |

快捷键 `Shift+Tab` 循环切换模式。

---

## 8. 常用工作流

### 新项目启动
```
claude
/init
/memory                    # 编辑生成的 CLAUDE.md
/mcp                       # 配置需要的 MCP 服务器
/agents                    # 创建项目专用子代理
```

### 日常编码
```
claude
"实现用户认证模块"         # Claude 自动探索 + 编码
/diff                      # 查看变更
/simplify                  # 优化代码
```

### 大范围重构
```
/plan 重构错误处理为 Result 模式
# 确认计划后
"执行计划"
/diff
/review
```

### 跨目录工作
```
/add-dir ../shared-lib
"修改 shared-lib 中的 API 并同步更新当前项目"
```
