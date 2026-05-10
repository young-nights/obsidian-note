---
name: embedded-bare-metal-development
description: |
  STM32 裸机嵌入式代码自主化工作流
  适用于 STM32F1/F4/F7/H7/G0 等系列（HAL 库 / 标准库均可）
  流程：用户需求 → 框架检测 → 结构化拆解 → 知识库检索 → 代码生成 → 审查测试 → 交付 + 经验沉淀
---

# STM32 Bare-Metal Development Workflow

## 1. 角色定位与信息流

| 步骤 | 执行者     | 目的                                         | 关键工具 / 指令                          | 输出物                |
|------|-----------|----------------------------------------------|------------------------------------------|-----------------------|
| 0    | main      | 检测工程框架类型（HAL / Standard Lib）         | read + grep on project files             | Framework Decision    |
| 1    | main      | 拆解用户需求，生成结构化任务单 + 需求文档       | -                                        | Task Brief            |
| 2    | clerk     | 从知识库检索 STM32 裸机相关经验               | memory_search + wiki_search              | Raw Experiences       |
| 3    | clerk     | 将原始经验转化为结构化摘要                     | code_execution                           | Structured Summary    |
| 4    | coder     | 基于摘要生成完整、可编译的代码工程             | sessions_send → coder                    | Full Project Code     |
| 5    | evaluator | 代码审查、静态分析、编译验证                   | sessions_send → evaluator + code_execution | Review Report         |
| 6    | main      | 最终交付 + 记录新经验                         | write + memory_learn                     | Delivered + Knowledge |

---

## 2. Step 0：框架检测（库类型判定）

> 主管 Agent 在拆解任务前，必须先判定目标工程使用 **HAL 库** 还是 **标准外设库（SPL/StdPeriph）**。

### 检测规则

```
IF 工程目录存在 → 执行以下检测：
  1. 查找 Drivers/STM32xx_HAL_Driver/ 目录或 stm32xx_hal.h 头文件
     → 命中 = HAL 库
  2. 查找 Libraries/STM32F10x_StdPeriph_Driver/ 或 stm32f10x_xxx.h 系列头文件
     → 命中 = 标准外设库
  3. 查找 CMSIS/ 且无 HAL/SPL 目录
     → 命中 = 纯 CMSIS 寄存器操作
  4. 以上均未命中
     → 视为新建工程，由主管根据芯片型号推荐（F1 → 标准库优先；F4+/H7/G0 → HAL 优先）
ELSE 无工程目录（全新项目）→ 根据芯片型号默认选择：
  - STM32F1 系列 → 标准外设库（SPL）
  - STM32F4/F7/H7/G0/G4/WB/U5 系列 → HAL 库
  - 用户有明确偏好则从用户
```

### 主管输出格式

```yaml
framework_decision:
  library: HAL | SPL | CMSIS_only
  chip_family: F1 | F4 | F7 | H7 | G0 | ...
  reason: "检测到 Drivers/STM32F4xx_HAL_Driver/ 目录，确认为 HAL 库工程"
  detection_method: "directory_scan" | "user_specified" | "default_recommendation"
```

---

## 3. Step 1：主管拆解需求

接收用户模糊需求后，主管必须输出以下内容：

### 3.1 Task Brief（YAML，必填）

```yaml
project_name: 
chip: STM32F407IGT6
library: HAL | SPL               # 来自 Step 0 检测结果
peripherals: [TIM, UART, GPIO, ADC, SPI, I2C, DMA, ...]
clock_config:
  hse_freq: 8MHz
  sysclk: 168MHz
  apb1: 42MHz
  apb2: 84MHz
requirements:
  - "TIM2 1ms 中断调度，驱动 8 路定时任务"
  - "UART1 DMA 空闲中断接收，环形缓冲区 256B"
  - "ADC1 三通道 DMA 连续采样，1kHz"
constraints:
  - "RAM < 128KB"
  - "禁止使用操作系统"
  - "中断优先级：TIM2 > UART > ADC"
  - "注释统一使用英文"
expected_output: 完整可编译的裸机工程代码，含 main.c、驱动层、业务层、配置文件
```

### 3.2 必须创建的文档

存放在工程根目录 `docs/` 下：

| 文档名               | 内容                         | 必填 |
|-----------------------|------------------------------|------|
| 业务逻辑需求.md        | 功能描述、状态机、数据流      | ✅   |
| 测试用例.md            | 模块测试 + 集成测试用例       | ✅   |
| 通讯协议.md            | 仅涉及外设/模块间通信时创建   | 条件 |
| 硬件引脚分配表.md      | GPIO 复用、外设引脚映射       | ✅   |

---

## 4. Step 2-3：Clerk 检索 & 结构化摘要

### 知识库路径

- **LLM Wiki 知识库**：`/home/whites/knowledge-llm-wiki/Embedded/`
- **原始资料目录**：`/home/whites/knowledge-llm-wiki/Embedded/raw/`（用户放入新资料）
- **结构化 Wiki**：`/home/whites/knowledge-llm-wiki/Embedded/wiki/`（LLM 编译维护）
- **Schema 规则**：`/home/whites/knowledge-llm-wiki/Embedded/schema.md`

### 检索策略

Clerk 执行三通道检索：

```python
# 1. LLM Wiki 知识库检索（使用 llm-wiki-embedded skill 的 Query 操作）
# 先检查 raw/ 是否有未 Ingest 的新文件，有则先执行 Ingest
wiki_query = [
    f"STM32 {chip_family} {library} bare-metal {peripheral}",
    f"STM32 {peripheral} interrupt DMA",
    f"{peripheral} driver template",
]

# 2. memory_search 检索历史项目经验
memory_keywords = [
    f"stm32 {chip_family} {library} bare-metal",
    f"stm32 {peripheral} {library} driver",
]

# 3. wiki_search 检索 ST 官方文档（如有网络）
wiki_search_keywords = [
    f"STM32 {chip_family} {library} {peripheral} configuration",
]
```

### Ingest 触发规则

> Clerk 在检索前，必须先检查 `raw/` 目录是否有未处理的新文件：
> 
> ```
> IF raw/ 中存在未 Ingest 的新文件（对比 wiki/ 中的 sources 字段）
> → 先执行 Ingest：读取 raw/ 新文件 → 提取关键知识 → 写入 wiki/ 结构化页面
> → 然后再执行 Query 检索
> ```

### Clerk 输出：Structured Summary

```markdown
## 技术摘要：{project_name}

### 库版本信息
- 库类型：{HAL/SPL}
- 固件包版本：STM32CubeFW_F4 V1.27.x / STM32F10x_StdPeriph_Lib V3.5.0
- CMSIS 版本：V5.x

### 外设驱动模板
#### {peripheral_name}
- 初始化函数原型
- 关键配置参数（时钟源、分频、中断/DMA 使能）
- 典型代码模板（含注释）
- 已知坑点与注意事项

### 时钟树配置要点
- HSE/HSI 选择、PLL 倍频链路
- AHB/APB 分频

### 中断优先级建议
- NVIC 分组策略
- 各外设中断优先级排序

### 历史经验（来自 memory_search）
- 相关项目经验摘要
- 常见编译/运行错误及解决方案
```

---

## 5. Step 4：Coder 代码生成

### 工程目录结构

```
{project_name}/
├── Core/
│   ├── Inc/
│   │   ├── main.h
│   │   ├── stm32f4xx_hal_conf.h    # HAL 版
│   │   ├── stm32f4xx_it.h
│   │   ├── app_config.h            # 业务配置
│   │   └── drivers/                # 驱动层头文件
│   │       ├── drv_uart.h
│   │       ├── drv_timer.h
│   │       ├── drv_adc.h
│   │       └── ...
│   └── Src/
│       ├── main.c
│       ├── stm32f4xx_it.c
│       ├── system_stm32f4xx.c
│       ├── app/                    # 业务逻辑层
│       │   ├── app_task.c
│       │   ├── app_state_machine.c
│       │   └── ...
│       └── drivers/                # 驱动实现
│           ├── drv_uart.c
│           ├── drv_timer.c
│           ├── drv_adc.c
│           └── ...
├── Drivers/                        # HAL：STM32F4xx_HAL_Driver
│   ├── CMSIS/
│   └── STM32F4xx_HAL_Driver/
├── Middlewares/                    # 第三方中间件（如有）
├── MDK-ARM/ 或 STM32CubeIDE/      # 工程文件
├── docs/                           # 需求文档
├── .project / .cproject            # IDE 工程文件
└── README.md
```

> **SPL 版**差异：`Drivers/` 改为 `Libraries/STM32F10x_StdPeriph_Driver/`，头文件前缀改为 `stm32f10x_` 系列。

### 编码规范

1. **库 API 一致性**
   - HAL 版：统一使用 `HAL_xxx_Init()` / `HAL_xxx_Start()` / `HAL_xxx_IRQHandler()`
   - SPL 版：统一使用 `xxx_Init()` / `xxx_Cmd()` / 外设缩写前缀
   - 禁止混用 HAL 和 SPL 函数

2. **分层架构**
   ```
   main.c → app 层（业务逻辑）→ driver 层（外设封装）→ HAL/SPL 底层
   ```

3. **中断处理**
   - `stm32f4xx_it.c` 中只放 `HAL_xxx_IRQHandler()` 调用
   - 实际回调逻辑放在 driver 层 `HAL_xxx_xxxCallback()`

4. **时钟配置**
   - HAL 版：通过 `SystemClock_Config()` 函数（CubeMX 生成风格）
   - SPL 版：通过 `RCC_Configuration()` 函数

5. **注释语言**：统一英文（避免编码乱码）

6. **编译目标**
   - HAL 版：支持 Keil MDK-5 / STM32CubeIDE / IAR
   - SPL 版：支持 Keil MDK-4/5 / IAR

### 代码生成指令（发给 Coder）

```
Generate complete bare-metal STM32 project:
- Chip: {chip}
- Library: {HAL/SPL} v{version}
- Peripherals: {peripherals}
- Clock: {clock_config}
- Requirements: {requirements}
- Constraints: {constraints}
- Must compile directly in {IDE}
- Output: Full project directory tree + all source files
- Comments: English only, Doxygen style
```

---

## 6. Step 5：Evaluator 审查

### 审查维度

| 维度         | 检查项                                              | 权重 |
|-------------|-----------------------------------------------------|------|
| 编译正确性   | 无语法错误、头文件引用正确、链接无 undefined reference | 30%  |
| 库一致性     | 全工程统一使用 HAL 或 SPL，无混用                     | 20%  |
| 时钟配置     | SYSCLK/APB1/APB2 频率与 Task Brief 一致              | 15%  |
| 中断安全     | 优先级配置合理、无重入风险、volatile 正确使用          | 15%  |
| 内存安全     | 无缓冲区溢出、栈大小合理、DMA 缓冲区对齐              | 10%  |
| 代码规范     | 命名一致、英文注释、分层清晰                          | 10%  |

### 审查流程

1. **静态检查**：`grep` 扫描混用 HAL/SPL API、未声明函数、magic number
2. **编译验证**：如有工具链环境，执行 `scons` / `make` / IDE CLI 编译
3. **逻辑审查**：状态机完整性、中断回调链路、外设初始化顺序

### 迭代机制

- 失败 → 自动返回 Coder 修复（最多 3 轮）
- 每轮附带 Review Report：
  ```markdown
  ## Review Round {N}
  - Pass Rate: {X}%
  - Issues:
    - [Critical] {description}
    - [Warning] {description}
  - Fix Suggestions: [...]
  ```

---

## 7. Step 6：交付 + 经验沉淀

### 交付物清单

- [ ] 完整工程源码（可编译）
- [ ] `docs/` 下所有需求文档
- [ ] `README.md`（构建说明、引脚表、已知限制）
- [ ] Review Report

### 经验沉淀

1. 将本次完整经验写入 `memory/YYYY-MM-DD.md`
2. 内容包含：Task Brief + Structured Summary + 最终代码摘要 + Review 结果 + 踩坑记录
3. 如发现高复用模式，调用 `skill-creator` 沉淀为独立 skill

---

## 附录：HAL vs SPL 速查对照

| 操作             | HAL 库                                | SPL 库                              |
|-----------------|----------------------------------------|-------------------------------------|
| GPIO 输出高      | `HAL_GPIO_WritePin(GPIOx, Pin, SET)`  | `GPIO_SetBits(GPIOx, Pin)`         |
| GPIO 输出低      | `HAL_GPIO_WritePin(GPIOx, Pin, RESET)`| `GPIO_ResetBits(GPIOx, Pin)`       |
| UART 发送        | `HAL_UART_Transmit()`                 | `USART_SendData()` + flag polling  |
| UART DMA 接收    | `HAL_UARTEx_ReceiveToIdleDMA()`       | `USART_DMACmd()` + DMA 手动配置    |
| TIM 启动         | `HAL_TIM_Base_Start_IT()`             | `TIM_Cmd()` + `TIM_ITConfig()`     |
| ADC 单次转换     | `HAL_ADC_Start()` + `HAL_ADC_PollForConversion()` | `ADC_SoftwareStartConvCmd()` + `ADC_GetConversionValue()` |
| 时钟配置         | `SystemClock_Config()` (MX 生成)      | `RCC_Configuration()` (手动编写)   |
| 中断回调         | `HAL_xxx_xxxCallback()`               | 在 `stm32f10x_it.c` 中直接实现     |
| 外设初始化       | `HAL_xxx_Init(&handle)`               | `xxx_Init(&struct)` + `xxx_Cmd(ENABLE)` |
