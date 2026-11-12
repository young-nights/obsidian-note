---
title: OpenClaw 使用过程中的疑问与痛点
type: troubleshoot
tags: [openclaw, faq, pain-points, workflow]
created: 2026-05-10
updated: 2026-05-10 17:38
---

# OpenClaw 使用过程中的疑问与痛点

## Q1：同一个对话窗口聊多个项目，会不会混淆？

### 问题描述

在飞书私聊中，可能上一句在讨论 LED 闪烁工程，下一句又说鱼缸项目的水泵驱动。AI 是否会把不同项目的上下文混在一起，导致输出混乱？

### 答案

**会混淆。** AI 维护的是当前对话窗口的完整上下文历史，没有自动按项目分区的能力。

### 解决方案

| 方案 | 可靠性 | 操作方式 |
|------|--------|----------|
| **按项目分群聊** | ⭐⭐⭐ 最推荐 | 在飞书中为每个项目创建独立群聊，把 OpenClaw bot 加入，每个群聊维护独立上下文 |
| **前缀声明** | ⭐⭐ 依赖习惯 | 私聊中切换项目时，开头标注：`【LED 项目】PA8 延时改用 TIM2` |
| **靠 AI 自行判断** | ⭐ 不可靠 | 不推荐，容易混淆 |

### 推荐做法

1. 在飞书中创建项目专属群聊（如"LED 闪烁项目"、"智能鱼缸"）
2. 将 OpenClaw bot 加入各群
3. 项目相关讨论在对应群中进行
4. 私聊仅用于总调度、日常沟通、非项目事务

### 示例

```
飞书群聊 "LED 闪烁项目"：
  你：把 PA8 改成 PA15，闪烁频率加快到 200ms
  我：好的，修改 main.c 中的 GPIO 配置和延时参数...

飞书群聊 "智能鱼缸"：
  你：水泵的 PWM 占空比需要根据水温动态调整
  我：新增温度查表逻辑，PWM 范围 20%-80%...

私聊：
  你：现在有几个项目在进行中？
  我：当前有 LED 闪烁和智能鱼缸两个项目，各自在独立群聊中...
```

## Q2：使用了 Skills，为什么 OpenSpace 没有进行进化调用？

### 问题描述

在嵌入式开发工作流中使用了 `stm-bare-metal-development` / `stm-rt-thread-development` 等 Skills，但 OpenSpace 并没有自动参与技能进化。Skills 不是会自动进化吗？

### 答案

**OpenSpace 和 OpenClaw Skills 是两套独立的系统。** 它们之间不会自动联动。

### 两套系统的区别

| 维度 | OpenClaw Skills | OpenSpace |
|------|-----------------|-----------|
| 存放位置 | `~/.openclaw/workspace/skills/` 或 Obsidian Skills 目录 | OpenSpace MCP 服务器本地注册表 + 云端社区 |
| 调用方式 | 主管读取 SKILL.md → `sessions_spawn` 分发给子代理 | `openspace__execute_task` 委托任务 |
| 进化机制 | **无自动进化**，需手动修改 SKILL.md | 自动进化（FIX / DERIVED / CAPTURED） |
| 上传机制 | 无 | `openspace__upload_skill` 上传到云端 |

### 为什么这次没有进化

实际执行链路：

```
你 → 主管(main) → 读取 stm-bare-metal-development SKILL.md → sessions_spawn → coder 子代理
```

全程使用 OpenClaw 原生 subagent 机制，**没有调用 OpenSpace 的任何工具**（`openspace__execute_task` / `openspace__search_skills` / `openspace__fix_skill`），所以 OpenSpace 从未介入，自然不会触发进化。

### 如何让 OpenSpace 参与进化

方案一：在工作流中显式调用 `openspace__execute_task`

```
# 替代 sessions_spawn，用 OpenSpace 执行任务
openspace__execute_task(
  task="创建 STM32F103RCT6 LED 闪烁工程",
  workspace_dir="/home/whites/embedded_item/led-blink"
)
# 执行完后返回 evolved_skills（如有）
```

方案二：任务完成后再调 OpenSpace 沉淀经验

```
# coder 完成代码后，将经验交给 OpenSpace 沉淀为 skill
openspace__execute_task(
  task="将 LED 闪烁工程的代码模式沉淀为可复用的 skill"
)
```

### 当前状态

- 嵌入式开发工作流暂不切换到 OpenSpace（用户决定）
- Skills 的维护仍由主管手动修改 SKILL.md 完成
- 后续如需自动进化能力，再将 Step 4（Coder 代码生成）改为 `openspace__execute_task` 路径
