---
name: embedded-rt-thread-development
description: |
  STM32 + RT-Thread 嵌入式代码自主化工作流
  适用于 STM32F1/F4/F7/H7/G0 等系列 + RT-Thread v5.x / v4.1.x
  支持 RT-Thread Nano（精简版）与 Standard（标准版）两种形态，均基于 HAL 库
  流程：用户需求 → 框架检测 → 结构化拆解 → 知识库检索 → 代码生成 → 审查测试 → 交付 + 经验沉淀
---

# RT-Thread Workflow for STM32

## 1. 背景：RT-Thread 两种形态

RT-Thread 在 STM32 上有 **两种使用方式**，底层均基于 **HAL 库**（不使用标准外设库 SPL）：

| 特性              | Nano（精简版）                          | Standard（标准版）                       |
|-------------------|----------------------------------------|-----------------------------------------|
| 核心大小          | ~3KB ROM / ~1KB RAM                    | ~20KB+ ROM / ~4KB+ RAM                  |
| 组件              | 内核 + FinSH（可选）                    | 内核 + 设备框架 + 组件 + 软件包          |
| 创建方式          | RT-Thread Studio 或手动嵌入已有工程      | RT-Thread Studio 或 RT-Thread Env 工具   |
| CubeMX 关系       | ✅ 推荐使用 CubeMX 生成外设初始化代码    | ✅ 可使用 CubeMX 辅助配置                |
| 构建系统          | Keil/IAR/CubeIDE 原生（跟随 CubeMX 工程）| SCons + Kconfig（Env 工具）或 Studio     |
| 适用场景          | 已有裸机工程快速引入 RTOS、资源极受限     | 新项目、需要丰富组件、中等以上资源       |

> **关键点**：无论 Nano 还是 Standard，底层都是 HAL 库。  
> 当使用 CubeMX 生成代码后，可以 **混用 RT-Thread 设备框架（rt_device 接口）和 HAL 库 API**。  
> 这是 RT-Thread + STM32 开发的标准模式。

---

## 2. 角色定位与信息流

| 步骤 | 执行者     | 目的                                               | 关键工具 / 指令                          | 输出物                |
|------|-----------|---------------------------------------------------|------------------------------------------|-----------------------|
| 0    | main      | 检测工程形态（Nano/Standard）+ CubeMX 使用状态       | read + grep on project files             | Framework Decision    |
| 1    | main      | 拆解用户需求，生成结构化任务单 + 需求文档            | -                                        | Task Brief            |
| 2    | clerk     | 从知识库检索 STM32/RT-Thread 相关经验               | memory_search + wiki_search              | Raw Experiences       |
| 3    | clerk     | 将原始经验转化为结构化摘要                           | code_execution                           | Structured Summary    |
| 4    | coder     | 基于摘要生成完整、可编译的 RT-Thread 工程            | sessions_send → coder                    | Full Project Code     |
| 5    | evaluator | 代码审查、静态分析、编译验证                         | sessions_send → evaluator + code_execution | Review Report         |
| 6    | main      | 最终交付 + 记录新经验                               | write + memory_learn                     | Delivered + Knowledge |

---

## 3. Step 0：框架检测

> 主管 Agent 在拆解任务前，必须先判定：RT-Thread 形态（Nano/Standard）、CubeMX 是否介入、组件配置。

### 检测规则

```
IF 工程目录存在 → 执行以下检测：

  1. RT-Thread 形态检测（Nano vs Standard）：
     - 查找 rtconfig.h / Kconfig
       → 如果仅有 RT_USING_FINSH 无 RT_USING_DEVICE / RT_USING_COMPONENTS_INIT
         = Nano 版
       → 如果包含 RT_USING_DEVICE / RT_USING_IPC / RT_USING_COMPONENTS_INIT
         = Standard 版
     - Nano 版通常无 SConstruct，代码直接在 MDK/CubeIDE 工程中编译
     - Standard 版通常有 SConstruct + Kconfig + Env 工具链

  2. CubeMX 使用检测（关键）：
     - 查找 *.ioc 文件（CubeMX 工程文件）
       → 存在 = CubeMX 已用于代码生成
     - 查找 Drivers/STM32xx_HAL_Driver/ 目录
       → 存在 = HAL 库驱动已由 CubeMX 或手动集成
     - 查找 Core/Src/main.c 中的 MX_xxx_Init() 函数
       → 存在 = CubeMX 生成的外设初始化代码
     - 查找 CubeMX_Config/ 或 .cproject 中的 CubeMX 引用
     - 判定结论：
       ✅ CubeMX 生成 → 可混用 rt_device + HAL API（标准模式）
       ⚠️ 无 CubeMX → 手动 HAL 配置，需确认外设初始化完整性

  3. RT-Thread 版本检测：
     - 查找 rtthread.h / rtconfig.h 中的 RT_VERSION 宏
     - 或查找 rt-thread/ 目录下的 version 文件
     → 确认 v4.1.x / v5.x

  4. 组件检测（扫描 rtconfig.h 中 #define RT_USING_xxx）：
     - finsh / msh → 命令行调试
     - device → 设备驱动框架（Standard 专属）
     - ipc → 信号量/互斥/消息队列/邮箱
     - utest → 单元测试框架
     - dfs → 文件系统
     - lwip → 网络协议栈
     - sal → 套接字抽象层
     - ulog → 日志组件

  5. 构建系统检测：
     - 存在 SConstruct + SConscript → SCons / Env 构建（Standard 典型）
     - 仅有 MDK-ARM/*.uvprojx 或 CubeIDE/.project → IDE 原生（Nano 典型）

ELSE 无工程目录（全新项目）→ 默认选择：
  - RT-Thread 形态：Standard（更完整，推荐新项目）
  - CubeMX：✅ 使用（生成外设初始化代码）
  - RT-Thread 版本：v5.2.0（最新稳定版）
  - 构建系统：SCons + Kconfig + Env
```

### 主管输出格式

```yaml
framework_decision:
  project_state: existing | new
  rtt_edition: Nano | Standard
  rt_thread_version: v5.2.0 | v4.1.x | unknown
  cubemx_used: true | false
  cubemx_ioc_path: path/to/project.ioc        # 已有工程时
  hal_driver_path: Drivers/STM32F4xx_HAL_Driver/
  chip_family: F1 | F4 | F7 | H7 | G0 | ...
  build_system: scons_env | mdk_native | cubeide_native
  detected_components: [finsh, device, ipc, ...]
  mix_mode: "rt_device + HAL API"             # CubeMX 生成时的标准模式
  bsp_path: bsp/stm32/stm32f407-st-discovery/ # 已有工程时
  reason: "Standard 版 + CubeMX .ioc 检测到 + HAL 库 + SCons 构建 + finsh/device/ipc"
  detection_method: "directory_scan" | "user_specified" | "default_recommendation"
```

---

## 4. Step 1：主管拆解需求

接收用户模糊需求后，主管必须输出以下内容：

### 4.1 Task Brief（YAML，必填）

```yaml
project_name: smart-fish-tank
chip: STM32F407IGT6
rt_thread_edition: Standard | Nano          # 来自 Step 0 检测结果
rt_thread_version: v5.2.0
cubemx_used: true                           # 推荐 true：CubeMX 生成外设初始化
peripherals: [TIM, UART, GPIO, ADC, SPI, I2C, DMA]
components_needed: [finsh, device, ipc, utest]
thread_architecture:
  - { name: led_thread,     priority: 25, stack: 512, period: 500ms,  duty: LED heartbeat }
  - { name: sensor_thread,  priority: 20, stack: 1024, period: 100ms, duty: ADC read + filter }
  - { name: comm_thread,    priority: 15, stack: 2048, period: event, duty: UART protocol parse }
ipc_objects:
  - { type: mq,    name: sensor_mq,    capacity: 16,  usage: "sensor → comm" }
  - { type: sem,   name: uart_rx_sem,  usage: "ISR → comm_thread" }
  - { type: mutex, name: spi_mutex,    usage: "multi-thread SPI bus exclusive" }
clock_config:
  hse_freq: 8MHz
  sysclk: 168MHz
  apb1: 42MHz
  apb2: 84MHz
requirements:
  - "TIM2 1ms 中断驱动 8 路软件定时器"
  - "UART1 DMA 空闲中断接收 + 环形缓冲区"
  - "ADC1 三通道 DMA 连续采样 1kHz"
  - "FinSH msh 调试命令支持"
constraints:
  - "总 RAM 用量 < 64KB（含 RT-Thread 内核 + 线程栈）"
  - "线程栈大小需估算（参考 RT-Thread stack_check）"
  - "中断优先级：TIM2(High) > UART(Mid) > ADC(Low)"
  - "注释统一使用英文"
  - "CubeMX 生成底层外设初始化，rt_device 框架封装驱动层"
expected_output: 完整可编译的 RT-Thread 工程，含 main.c、rtconfig.h、board.c、驱动层、业务层
```

### 4.2 必须创建的文档

存放在工程根目录 `docs/` 下：

| 文档名               | 内容                                         | 必填 |
|-----------------------|----------------------------------------------|------|
| 业务逻辑需求.md        | 功能描述、状态机、数据流、线程协作关系          | ✅   |
| 线程架构设计.md        | 线程表、优先级、IPC 对象、时序图               | ✅   |
| 测试用例.md            | 模块测试 + 集成测试 + utest 用例              | ✅   |
| 通讯协议.md            | 仅涉及设备间/模块间通信时创建                  | 条件 |
| 硬件引脚分配表.md      | GPIO 复用、外设引脚映射                        | ✅   |

---

## 5. Step 2-3：Clerk 检索 & 结构化摘要

### 检索策略

```python
keywords = [
    f"stm32 {chip_family} rt-thread {rt_thread_edition} {rt_thread_version}",
    f"rt-thread cubemx {peripheral} device driver hal",
    f"rt-thread thread ipc {ipc_type} example",
    f"rt-thread Nano embed cubemx project",
    f"rt-thread finsh msh custom command",
    f"rt-thread DMA uart idle interrupt HAL",
    f"rt_device {peripheral} HAL callback",
]
# memory_search + wiki_search 双通道检索
```

### Clerk 输出：Structured Summary

```markdown
## 技术摘要：{project_name}

### 形态与配置
- 形态：{Nano/Standard}
- 版本：v{version}
- CubeMX：{已使用/未使用}
- 底层库：HAL（STM32Cube FW v{version}）
- 构建方式：{SCons+Env / MDK 原生 / CubeIDE}

### CubeMX + RT-Thread 混用模式
- CubeMX 负责：时钟树、外设初始化（GPIO/UART/DMA/TIM/ADC…）
- RT-Thread 负责：线程调度、IPC、设备驱动框架封装
- 混用关键：
  - CubeMX 生成的 `MX_xxx_Init()` 在 `board.c` 的 `rt_hw_board_init()` 中调用
  - rt_device 驱动层在 `HAL_xxx_Init()` 之上封装 `rt_device_xxx` 接口
  - ISR 回调（如 `HAL_UART_RxCpltCallback`）中通过 sem/mq 通知 RT-Thread 线程

### 线程设计模板
#### {thread_name}
- 创建方式：rt_thread_create() vs rt_thread_init()（动态 vs 静态）
- 栈大小估算方法
- 入口函数模板

### IPC 对象模板
#### {ipc_type}_{name}
- 创建与初始化 API
- 典型发送/接收模式
- 超时处理

### 设备驱动框架（rt_device）
- rt_device_find() → rt_device_open() → rt_device_read/write()
- UART 设备注册与 HAL DMA 接收集成
- ADC 设备配置与 HAL DMA 采样集成

### Nano 版嵌入指南（如适用）
- 添加 rt-thread/src/ + rt-thread/include/ 到工程
- 修改 board.c 实现 rt_hw_board_init()
- 实现 SysTick → rt_tick_increase()
- 实现 rt_hw_console_output() → 重定向到 UART

### Kconfig 配置模板（Standard 版）
- 芯片选择、时钟配置、外设使能
- RT-Thread 组件裁剪

### SConscript 编写规则（Standard 版）
- 源文件扫描、头文件路径、链接脚本

### 历史经验（来自 memory_search）
- 相关项目经验摘要
- 常见坑点（栈溢出、优先级反转、DMA cache 一致性、CubeMX 重生成覆盖等）
```

---

## 6. Step 4：Coder 代码生成

### 6.1 Nano 版工程结构

```
{project_name}/
├── Core/
│   ├── Inc/
│   │   ├── main.h
│   │   ├── stm32f4xx_hal_conf.h
│   │   ├── stm32f4xx_it.h
│   │   ├── app_config.h
│   │   └── drivers/
│   │       ├── drv_uart.h
│   │       └── ...
│   └── Src/
│       ├── main.c                      # CubeMX 生成 + RT-Thread 启动
│       ├── stm32f4xx_it.c
│       ├── stm32f4xx_hal_msp.c         # CubeMX 生成的 MSP 初始化
│       ├── system_stm32f4xx.c
│       ├── app/                        # 业务线程
│       │   ├── app_task.c
│       │   └── ...
│       └── drivers/                    # rt_device 封装驱动
│           ├── drv_uart.c
│           └── ...
├── Drivers/
│   ├── CMSIS/
│   └── STM32F4xx_HAL_Driver/           # CubeMX 生成的 HAL 驱动
├── rt-thread/                          # RT-Thread Nano 源码（精简）
│   ├── include/
│   ├── src/
│   │   ├── clock.c
│   │   ├── ipc.c
│   │   ├── irq.c
│   │   ├── kservice.c
│   │   ├── mem.c / memheap.c / slab.c
│   │   ├── object.c
│   │   ├── scheduler.c
│   │   ├── thread.c
│   │   ├── timer.c
│   │   └── components.c
│   └── components/
│       └── finsh/                      # 可选
├── MDK-ARM/ 或 STM32CubeIDE/           # CubeMX 生成的 IDE 工程
├── *.ioc                               # CubeMX 工程文件
├── docs/
└── README.md
```

### 6.2 Standard 版工程结构

```
{project_name}/
├── applications/
│   ├── main.c                          # rt_application_init() 入口
│   ├── app_task.c                      # 业务线程实现
│   ├── app_state_machine.c
│   └── app_config.h
├── drivers/
│   ├── board.c                         # rt_hw_board_init() → 调用 CubeMX 的 SystemClock_Config()
│   ├── board.h
│   ├── drv_uart.c                      # rt_device 封装，内部调用 HAL API
│   ├── drv_uart.h
│   ├── drv_adc.c
│   ├── drv_timer.c
│   ├── drv_gpio.c
│   ├── drv_spi.c
│   └── pin_map.h
├── libraries/                          # HAL 驱动库（CubeMX 集成或手动）
│   ├── CMSIS/
│   └── STM32F4xx_HAL_Driver/
├── CubeMX_Config/                      # CubeMX .ioc + 生成的代码备份（可选）
├── bsp/                                # BSP 配置
├── rt-thread/                          # RT-Thread Standard 完整源码
│   ├── include/
│   ├── src/
│   └── components/
├── Kconfig
├── SConstruct
├── SConscript
├── rtconfig.h
├── rtconfig.py
├── .config
├── docs/
└── README.md
```

### 6.3 CubeMX + RT-Thread 混用编码规范

1. **职责划分**
   ```
   CubeMX 生成层（不要手动修改）：
     SystemClock_Config() / MX_GPIO_Init() / MX_UART1_Init() / MX_DMA_Init() / ...
     → stm32f4xx_hal_msp.c（MSP 初始化）
     → stm32f4xx_it.c（IRQHandler，仅调用 HAL_xxx_IRQHandler）

   RT-Thread 适配层（手动编写）：
     board.c → rt_hw_board_init() 中调用 SystemClock_Config() + HAL_Init()
     drv_xxx.c → 封装 HAL API 为 rt_device 接口

   应用层（业务逻辑）：
     app_task.c → RT-Thread 线程 + IPC
   ```

2. **驱动编写规则（rt_device + HAL 混用）**
   ```c
   // UART 设备驱动示例
   static rt_err_t uart_init(rt_device_t dev) {
       // HAL 初始化已由 CubeMX 的 MX_UART1_Init() 完成
       // 这里只需：使能空闲中断 + 启动 DMA 接收
       __HAL_UART_ENABLE_IT(&huart1, UART_IT_IDLE);
       HAL_UART_Receive_DMA(&huart1, rx_buf, RX_BUF_SIZE);
       return RT_EOK;
   }

   static rt_ssize_t uart_read(rt_device_t dev, rt_off_t pos, void *buffer, rt_size_t size) {
       // 从环形缓冲区读取数据
       return ringbuffer_read(&rb, buffer, size);
   }

   // ISR 回调（在 stm32f4xx_it.c 的 UART1_IRQHandler 中被 HAL 调用）
   void HAL_UART_IdleCallback(UART_HandleTypeDef *huart) {
       if (huart->Instance == USART1) {
           uint16_t len = RX_BUF_SIZE - __HAL_DMA_GET_COUNTER(huart1.hdmarx);
           ringbuffer_write(&rb, rx_buf, len);
           rt_sem_release(uart_rx_sem);    // 通知 RT-Thread 线程
           HAL_UART_Receive_DMA(&huart1, rx_buf, RX_BUF_SIZE); // 重启 DMA
       }
   }
   ```

3. **Nano 版关键实现**
   ```c
   // board.c
   void rt_hw_board_init() {
       HAL_Init();                          // HAL 初始化
       SystemClock_Config();                // CubeMX 生成的时钟配置
       // ... 外设初始化由 CubeMX 的 main() 中的 MX_xxx_Init() 完成

       /* SysTick 配置：RT-Thread 的 tick 源 */
       HAL_SYSTICK_Config(HAL_RCC_GetHCLKFreq() / RT_TICK_PER_SECOND);

       /* UART 控制台（FinSH） */
       #ifdef RT_USING_FINSH
       rt_console_set_device(RT_CONSOLE_DEVICE_NAME);
       #endif
   }

   // SysTick 中断（RT-Thread tick 驱动）
   void SysTick_Handler(void) {
       HAL_IncTick();                       // HAL tick
       rt_tick_increase();                  // RT-Thread tick
   }

   // UART 控制台输出
   void rt_hw_console_output(const char *str) {
       rt_size_t i = 0, size = 0;
       char a = '\r';
       size = rt_strlen(str);
       for (i = 0; i < size; i++) {
           if (*(str + i) == '\n') {
               HAL_UART_Transmit(&huart1, (uint8_t *)&a, 1, 1);
           }
           HAL_UART_Transmit(&huart1, (uint8_t *)(str + i), 1, 1);
       }
   }
   ```

4. **中断处理规则**
   - `stm32f4xx_it.c` 中 `IRQHandler` 只调用 `HAL_xxx_IRQHandler()`
   - HAL 回调函数（`HAL_xxx_xxxCallback`）放在对应 `drv_xxx.c` 中
   - 回调函数中通过 `rt_sem_release()` / `rt_mq_send()` 通知线程
   - 禁止在 ISR 中调用 `rt_malloc()`、`rt_thread_mdelay()` 等阻塞 API

5. **CubeMX 重生成注意事项**
   - CubeMX 会覆盖 `Core/Src/main.c` 中 `USER CODE BEGIN/END` 之外的代码
   - 所有自定义代码必须写在 `/* USER CODE BEGIN ... */` 和 `/* USER CODE END ... */` 之间
   - RT-Thread 启动代码放在 `USER CODE BEGIN 2` 中
   - 驱动层代码放在 `drivers/` 目录，不受 CubeMX 重生成影响

6. **注释语言**：统一英文

7. **编译目标**
   - Nano 版：Keil MDK-5 / STM32CubeIDE / IAR（跟随 CubeMX 工程）
   - Standard 版：`scons --target=mdk5` / `scons --target=stm32cubeide` / `scons`（GCC）

### 6.4 代码生成指令（发给 Coder）

```
Generate complete RT-Thread {Nano/Standard} STM32 project:
- Chip: {chip}
- RT-Thread: {rt_thread_edition} v{version}
- CubeMX: {used/not_used} — generate HAL peripheral init + .ioc
- Peripherals: {peripherals}
- Components: {components}
- Thread Architecture: {thread_table}
- IPC Objects: {ipc_table}
- Clock: {clock_config}
- Requirements: {requirements}
- Constraints: {constraints}
- Mix Mode: rt_device framework wrapping HAL API (CubeMX-generated init)
- Build: {scons_env / mdk5 / cubeide}
- Output: Full project directory tree + all source files
- Comments: English only, Doxygen style
- All custom code must be within USER CODE BEGIN/END markers (CubeMX safe)
```

---

## 7. Step 5：Evaluator 审查

### 审查维度

| 维度               | 检查项                                                          | 权重 |
|-------------------|-----------------------------------------------------------------|------|
| 编译正确性         | 无语法错误、头文件引用正确、链接无 undefined reference            | 20%  |
| CubeMX 兼容性      | 自定义代码在 USER CODE 区域、重生成不覆盖业务逻辑                 | 15%  |
| RT-Thread 规范     | 线程创建/启动正确、IPC 使用无死锁风险、设备框架使用正确           | 20%  |
| 线程安全           | 共享资源有保护、ISR 无阻塞调用、优先级无反转                      | 15%  |
| 栈安全             | 各线程栈大小合理、启用溢出检测、预留安全余量                      | 10%  |
| HAL/rt_device 边界 | CubeMX 生成的 MX_xxx_Init 不被手动修改、rt_device 封装完整        | 10%  |
| 代码规范           | 命名一致、英文注释、分层清晰                                     | 10%  |

### 审查流程

1. **CubeMX 一致性检查**
   - 扫描 `USER CODE BEGIN/END` 区域外是否有手动添加的代码
   - 确认 `*.ioc` 文件中配置与 `rtconfig.h` 使能的外设一致
   - 确认 `SystemClock_Config()` 输出频率与 Task Brief 一致

2. **静态检查**
   - ISR 中的阻塞 API（rt_malloc、rt_thread_mdelay、rt_mutex_take）
   - 线程栈大小是否低于 256 字节（危险阈值）
   - IPC 对象是否在使用前完成创建/初始化
   - `RT_USING_xxx` 与代码引用的一致性

3. **配置验证（Standard 版）**
   - `rtconfig.h` 中 `RT_MAIN_THREAD_STACK_SIZE` ≥ 2048
   - `RT_TIMER_THREAD_STACK_SIZE` ≥ 512
   - `RT_TICK_PER_SECOND` 与 Task Brief 一致
   - `RT_THREAD_PRIORITY_MAX` ≥ 实际最大优先级

4. **编译验证**
   - Nano 版：检查 MDK/CubeIDE 工程文件完整性
   - Standard 版：执行 `scons --target=mdk5` 后验证工程可打开

### 迭代机制

- 失败 → 自动返回 Coder 修复（最多 3 轮）
- 每轮附带 Review Report：
  ```markdown
  ## Review Round {N}
  - Pass Rate: {X}%
  - Issues:
    - [Critical] sensor_thread 栈仅 256B — 溢出风险
    - [Critical] CubeMX USER CODE 区域外有手动修改 — 重生成将丢失
    - [Warning] 未启用 RT_USING_OVERFLOW_CHECK
    - [Warning] drv_uart.c 中 HAL 回调未在 USER CODE 区域保护
  - Fix Suggestions: [...]
  ```

---

## 8. Step 6：交付 + 经验沉淀

### 交付物清单

- [ ] 完整工程源码
  - Nano 版：可直接用 Keil/CubeIDE 打开编译
  - Standard 版：可通过 `scons --target=mdk5` 生成并编译
- [ ] `rtconfig.h`（最终配置快照）
- [ ] `*.ioc`（CubeMX 工程文件）
- [ ] `docs/` 下所有需求文档
- [ ] `README.md`（构建说明、线程表、引脚表、CubeMX 重生成说明、已知限制）
- [ ] Review Report

### 经验沉淀

1. 将本次完整经验写入 `memory/YYYY-MM-DD.md`
2. 内容包含：Task Brief + Structured Summary + 最终代码摘要 + Review 结果 + 踩坑记录
3. 如发现高复用模式，调用 `skill-creator` 沉淀为独立 skill

---

## 附录 A：RT-Thread 常用 API 速查

| 操作             | API                                          | 注意事项                          |
|-----------------|----------------------------------------------|----------------------------------|
| 创建线程         | `rt_thread_create(name, entry, param, stack, prio, tick)` | 动态分配栈，需检查返回 NULL     |
| 初始化线程       | `rt_thread_init(thread, name, entry, param, stack, size, prio, tick)` | 静态分配，栈数组需 word 对齐   |
| 启动线程         | `rt_thread_startup(thread)`                  | create/init 后必须调用          |
| 线程延时         | `rt_thread_mdelay(ms)`                       | 不要用裸机 for-loop 延时        |
| 信号量创建       | `rt_sem_create(name, init_value)`            | ISR→Thread 通信用 sem           |
| 信号量获取       | `rt_sem_take(sem, timeout)`                  | ISR 中禁止使用                  |
| 信号量释放       | `rt_sem_release(sem)`                        | ISR 中可用                      |
| 消息队列创建     | `rt_mq_create(name, msg_size, max_msgs, flag)` | msg_size 为单条消息字节数      |
| 消息队列发送     | `rt_mq_send(mq, buf, size)`                  | ISR 中可用                      |
| 消息队列接收     | `rt_mq_recv(mq, buf, size, timeout)`         | ISR 中禁止使用                  |
| 互斥量创建       | `rt_mutex_create(name, flag)`                | 不在 ISR 中使用，支持优先级继承  |
| 互斥量获取       | `rt_mutex_take(mutex, timeout)`              | 禁止在 ISR 中调用               |
| 事件集           | `rt_event_create(name, flag)`                | 支持 AND/OR 等待模式             |
| 事件发送         | `rt_event_send(event, set)`                  | ISR 中可用                      |
| 事件接收         | `rt_event_recv(event, set, opt, timeout, recved)` | ISR 中禁止使用               |
| 设备查找         | `rt_device_find(name)`                       | 返回设备句柄，NULL 表示未找到    |
| 设备打开         | `rt_device_open(dev, flag)`                  | flag: RT_DEVICE_FLAG_xxx        |
| 设备读写         | `rt_device_read/write(dev, pos, buf, size)`  | 返回实际读写字节数              |
| 动态内存         | `rt_malloc(size)` / `rt_free(ptr)`           | 不在 ISR 中使用                 |
| 定时器创建       | `rt_timer_create(name, handler, param, tick, flag)` | flag: RT_TIMER_FLAG_xxx     |
| 定时器启动       | `rt_timer_start(timer)`                      | 创建后需手动启动                |
| 进入临界区       | `rt_enter_critical()` / `rt_exit_critical()` | 保护极短临界区                  |

## 附录 B：CubeMX + RT-Thread 混用要点

### 职责划分图

```
┌─────────────────────────────────────────────────┐
│              Application Layer                   │
│  app_task.c — RT-Thread 线程 + IPC               │
├─────────────────────────────────────────────────┤
│            RT-Thread Device Framework            │
│  drv_uart.c / drv_adc.c — rt_device 接口封装      │
│  rt_device_find/open/read/write/control           │
├─────────────────────────────────────────────────┤
│              HAL Driver Layer                    │
│  HAL_UART_Init() / HAL_ADC_Start_DMA() / ...     │
│  ← CubeMX 生成，不要手动修改                       │
├─────────────────────────────────────────────────┤
│              CMSIS / Hardware                    │
│  寄存器操作、NVIC、SysTick                        │
└─────────────────────────────────────────────────┘
```

### CubeMX 重生成安全规则

1. **永远不要修改** `main.c` 中 `USER CODE` 区域外的代码
2. **RT-Thread 启动**放在 `USER CODE BEGIN 2`：
   ```c
   /* USER CODE BEGIN 2 */
   extern int rt_application_init(void);
   rt_application_init();
   /* USER CODE END 2 */
   ```
3. **驱动层代码**放在 `drivers/` 目录，CubeMX 不会触及
4. **业务层代码**放在 `applications/` 目录，CubeMX 不会触及
5. 重生成后只需确认 `MX_xxx_Init()` 调用顺序和参数正确

## 附录 C：常见坑点

| 问题                     | 原因                                       | 解决方案                              |
|-------------------------|--------------------------------------------|---------------------------------------|
| 线程栈溢出              | 栈大小估算不足                               | 启用 `RT_USING_OVERFLOW_CHECK`，使用 `list_thread` 查看栈使用率 |
| 优先级反转              | 低优先级线程持锁被中优先级抢占               | 使用 `rt_mutex_create`（内置优先级继承） |
| ISR 中调用阻塞 API      | ISR 不应阻塞                                | ISR 只做 sem/mq/event 发送，逻辑放到线程 |
| CubeMX 重生成覆盖代码   | 自定义代码写在 USER CODE 区域外              | 严格遵守 USER CODE BEGIN/END 标记     |
| DMA cache 一致性        | Cortex-M7 有 D-Cache                       | 使用 non-cacheable 区域或 SCB_Clean/Invalidate |
| FinSH 命令无输出        | UART 设备未注册或未 open                    | 检查 `rt_console_set_device()` 调用   |
| scons 编译报错          | Kconfig 未配置或 rtconfig.h 过期            | 先执行 `menuconfig` 重新生成配置      |
| 线程创建返回 RT_NULL    | 内存不足                                    | 增大 `RT_HEAP_SIZE` 或改用静态初始化   |
| Nano 版 tick 不走       | SysTick_Handler 中未调用 `rt_tick_increase()` | 确保 SysTick_Handler 同时调用 HAL_IncTick + rt_tick_increase |
| HAL 回调与 rt_device 脱节 | 驱动层未正确桥接 HAL 回调到 rt_device 通知  | 回调中使用 rt_sem/rt_mq 通知设备消费者 |
| UART DMA 丢数据        | 空闲中断未正确清标志 + DMA 未重启            | 回调中先读 DMA 剩余计数，再重启 DMA    |
