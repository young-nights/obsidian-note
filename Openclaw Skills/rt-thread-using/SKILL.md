---
name: rt-thread-workflow
description: |
  STM32 + RT-Thread 嵌入式代码自主化工作流
  适用于 STM32F1/F4/F7/H7/G0 等系列 + RT-Thread 最新稳定版（v5.x / v4.1.x）。
  目标：用户提出需求 → 自动检索历史经验 → 生成可直接编译运行的完整工程代码 → 审查测试 → 交付 + 沉淀新经验。
---

# RT-Thread Workflow for STM32

## 1. 角色定位与信息流

| 步骤 | 执行者      | 目的                                   | 关键工具 / 指令                          | 输出物                  |
|------|------------|----------------------------------------|------------------------------------------|-------------------------|
| 1    | main       | 拆解用户需求，生成结构化任务单         | -                                        | Task Brief              |
| 2    | clerk      | 从知识库检索 STM32/RT-Thread 相关经验 | memory_search + wiki_search              | Raw Experiences         |
| 3    | clerk      | 将原始经验转化为结构化摘要             | code_execution（文本抽取 + Markdown）    | Structured Summary      |
| 4    | coder      | 基于摘要生成完整、可编译的代码工程     | sessions_send → coder                    | Full Project Code       |
| 5    | evaluator  | 代码审查、静态分析、单元测试模拟       | sessions_send → evaluator + code_execution | Review Report + Test Result |
| 6    | main       | 最终交付 + 记录新经验                 | write_file + skill-creator + memory_learn | Delivered Code + New Knowledge |


## 2. 详细工作流（自动循环执行）

### Step 0：主管拆解（你手动触发）
- 接收用户需求（例如：“实现一个使用 RT-Thread 的 UART DMA 接收 + 线程间消息队列通信的 LED 闪烁项目”）
- 输出结构化 **Task Brief**（必须包含以下字段）：

  ```yaml
  project_name: 
  chip: STM32F407IGT6          # 或具体型号
  rt-thread_version: v5.2.0
  peripherals: [UART, DMA, GPIO]
  components_needed: [finsh, utest, device, ipc]
  requirements: [...]
  constraints: [RAM < 64KB, 优先使用 RT-Thread 标准 API]
  expected_output: 完整可编译的 RT-Thread 工程代码，包含 main.c、rtconfig.h、组件配置等
  ```

### Step 1-2：Clerk 检索 & 摘要（自动）
- 使用 memory_search 关键词：stm32 + rt-thread + {peripheral} + {feature}
- 使用 wiki_search 查询官方文档（RT-Thread 官网、STM32 HAL 手册）
- 提取关键经验：Kconfig 配置、SConscript 写法、典型驱动模板、常见坑点（时钟配置、DMA 中断优先级等）
- 输出 Structured Summary（Markdown 格式，包含代码片段模板）


### Step 3：Coder 生成代码（自动）

**提示词要求：**
1. 必须生成完整工程结构（包括 .c/.h、Kconfig、SConscript、rtconfig.h、main.c、board.c 等）
2. 严格使用 RT-Thread 标准 API（rt_thread_create、rt_mq_send、rt_device 等）
3. 包含详细中文注释 + doxygen 风格
4. 支持 scons --target=mdk5 或 stm32cubeide 直接编译

输出方式：通过 sessions_send 发送给专用 Coder Agent


### Step 4：Evaluator 审查测试（自动）
- 代码审查：检查是否符合 RT-Thread 编程规范，是否符合命名规范、内存安全、RTOS 最佳实践（避免栈溢出、死锁），是否有明显的逻辑错误
- 静态分析：使用工具（如 cppcheck）扫描潜在的内存泄漏、未初始化变量、死代码等
- 单元测试模拟：如果包含 utest 组件，模拟运行测试用例，检查功能正确性 

如果失败 → 自动返回给 Coder 迭代（最多 3 轮）
输出 Review Report（通过率、问题列表、修复建议）


### Step 5：最终交付 + 沉淀新经验（自动）

- 将通过审查的代码写入用户指定目录
- 使用 memory_learn 记录本次完整经验（Task Brief + Summary + Final Code + Review）
- 可选：调用 skill-creator 将高价值模式沉淀为新 skill

