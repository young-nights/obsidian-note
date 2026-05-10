---
name: cms-embedded-development
description: |
  CMS（中微半导体）嵌入式代码自主化工作流
  适用于 CMS8S/CMS80F（8051 内核）及 CMS32M/CMS32L（ARM Cortex-M0/M0+）全系列
  流程：用户需求 → 芯片判定 → 框架检测 → 结构化拆解 → 知识库检索 → 代码生成 → 审查测试 → 交付 + 经验沉淀
---

# CMS (中微半导体) Embedded Development Workflow

## 1. 角色定位与信息流

| 步骤 | 执行者     | 目的                                         | 关键工具 / 指令                          | 输出物                |
|------|-----------|----------------------------------------------|------------------------------------------|-----------------------|
| 0    | main      | 芯片系列判定 + 开发环境检测                    | read + grep on project files             | Chip & Env Decision   |
| 1    | main      | 拆解用户需求，生成结构化任务单 + 需求文档       | -                                        | Task Brief            |
| 2    | clerk     | 从知识库检索 CMS 相关经验与寄存器配置           | memory_search + wiki_search              | Raw Experiences       |
| 3    | clerk     | 将原始经验转化为结构化摘要                     | code_execution                           | Structured Summary    |
| 4    | coder     | 基于摘要生成完整、可编译的代码工程             | sessions_send → coder                    | Full Project Code     |
| 5    | evaluator | 代码审查、静态分析、编译验证                   | sessions_send → evaluator + code_execution | Review Report         |
| 6    | main      | 最终交付 + 记录新经验                         | write + memory_learn                     | Delivered + Knowledge |

---

## 2. 芯片系列与内核架构判定

> CMS 半导体有两大产品线，内核架构完全不同，必须先判定再动手。

### 2.1 芯片系列速查

| 系列 | 内核 | 编译器 | 典型型号 | 主要用途 |
|------|------|--------|----------|----------|
| **CMS8S** | 8051 | Keil C51 | CMS8S6990, CMS8S6980 | 通用控制、消费电子 |
| **CMS80F** | 8051 增强型 | Keil C51 | CMS80F7X 系列 | 高性能 8 位控制 |
| **CMS32M67xx** | ARM Cortex-M0 | Keil MDK / GCC ARM | CMS32M6710, CMS32M6720 | 电机控制（FOC） |
| **CMS32L052** | ARM Cortex-M0+ | Keil MDK / GCC ARM | CMS32L052xx | 低功耗 IoT / 传感器 |
| **CMS79F** | 8051 | Keil C51 | CMS79F 系列 | 触摸按键、小家电 |

### 2.2 判定流程

```
IF 工程目录存在 → 执行以下检测：
  1. 查找芯片型号（Makefile / .uvprojx / .ioc 中的 DEVICE 或 MCU 声明）
     - 包含 "CMS8S" 或 "CMS80F" → 8051 系列
     - 包含 "CMS32M" → ARM 电机控制系列
     - 包含 "CMS32L" → ARM 低功耗系列
     - 包含 "CMS79F" → 8051 触摸系列
  2. 查找启动文件
     - startup_xxx.s (Keil C51 格式) → 8051
     - startup_xxx.s (ARM 汇编 .syntax unified) → ARM
  3. 查找链接脚本
     - .lkf 文件 → 8051 (Keil C51)
     - .ld 文件 (MEMORY { FLASH ... }) → ARM (GCC)
     - .sct 文件 (scatter-loading) → ARM (Keil MDK)
  4. 以上均未命中 → 视为新建工程，由主管根据用户指定的芯片型号判定
ELSE 无工程目录（全新项目）→ 用户必须提供芯片型号，否则询问
```

### 2.3 主管输出格式

```yaml
chip_decision:
  chip_family: CMS8S | CMS80F | CMS32M | CMS32L | CMS79F
  core: 8051 | cortex-m0 | cortex-m0plus
  compiler: keil_c51 | keil_mdk | gcc_arm
  reason: "检测到 Makefile 中 DEVICE=CMS32M6710，确认为 ARM Cortex-M0 电机控制系列"
  detection_method: "directory_scan" | "user_specified" | "prompt_required"
```

---

## 3. 项目创建工作区规范

### 3.1 目录定义

| 目录 | 路径 | 用途 | 权限 |
|------|------|------|------|
| **库文件目录** | `/home/whites/embedded_lib/` | 存放所有 CMS SDK / 库文件 | **只读**，禁止修改 |
| **工程项目目录** | `/home/whites/embedded_item/` | 存放所有新建工程 | 读写，可自由创建 |

### 3.2 CMS SDK 目录结构参考

#### 8051 系列 (CMS8S / CMS80F / CMS79F)

```
embedded_lib/cms-8051-sdk/
├── Include/
│   ├── CMS8S6990.h              # 芯片寄存器定义（核心文件）
│   ├── stdint_c51.h             # C51 标准整型
│   └── intrins.h                # 内联汇编支持
├── Startup/
│   ├── STARTUP.A51              # Keil C51 启动代码
│   └── CMS8S6990.LIB            # 预编译库（如有）
├── DriverLib/                   # 外设驱动库（如有）
│   ├── gpio/
│   ├── uart/
│   ├── timer/
│   ├── adc/
│   ├── pwm/
│   └── i2c/
└── Examples/                    # 官方示例（仅参考）
```

#### ARM 系列 (CMS32M / CMS32L)

```
embedded_lib/cms32-sdk/
├── CMSIS/
│   ├── Include/                 # core_cm0.h, core_cm0plus.h
│   └── Device/
│       └── CMS32M67xx/
│           ├── Include/         # CMS32M67xx.h, system_CMS32M67xx.h
│           └── Source/
│               ├── ARM/         # startup_CMS32M67xx.s (Keil)
│               └── GCC/         # startup_CMS32M67xx.s (GCC)
├── DriverLib/                   # 外设驱动库
│   ├── inc/
│   │   ├── cms32m67xx_gpio.h
│   │   ├── cms32m67xx_uart.h
│   │   ├── cms32m67xx_timer.h
│   │   ├── cms32m67xx_adc.h
│   │   ├── cms32m67xx_pwm.h
│   │   ├── cms32m67xx_i2c.h
│   │   └── cms32m67xx_clock.h
│   └── src/
│       ├── cms32m67xx_gpio.c
│       ├── cms32m67xx_uart.c
│       └── ...
├── MotorControl/                # CMS32M67xx 专用电机 FOC 库（如有）
│   ├── foc/
│   └── mcpwm/
└── Examples/
```

### 3.3 创建新工程流程

```
1. 在 /home/whites/embedded_item/ 下创建工程目录
   mkdir -p /home/whites/embedded_item/{project_name}/

2. 从 embedded_lib/ 复制需要的库文件到工程内
   # 8051 示例：
   cp embedded_lib/cms-8051-sdk/Include/CMS8S6990.h embedded_item/{project_name}/Libraries/Include/
   cp embedded_lib/cms-8051-sdk/Startup/STARTUP.A51 embedded_item/{project_name}/Libraries/Startup/

   # ARM 示例：
   cp -r embedded_lib/cms32-sdk/CMSIS/ embedded_item/{project_name}/Libraries/CMSIS/
   cp embedded_lib/cms32-sdk/DriverLib/inc/*.h embedded_item/{project_name}/Libraries/DriverLib/inc/
   cp embedded_lib/cms32-sdk/DriverLib/src/cms32m67xx_gpio.c embedded_item/{project_name}/Libraries/DriverLib/src/

3. 编写业务代码（main.c, app/, drivers/ 等）

4. 链接脚本 / 散点文件放在工程根目录

5. 构建文件中所有 include 路径指向工程内部 Libraries/ 目录
   # ✅ 正确：-ILibraries/DriverLib/inc
   # ❌ 错误：-I/home/whites/embedded_lib/...

6. 编译验证：make 或通过 IDE 构建
```

### 3.4 铁律

1. **库文件只读**：`/home/whites/embedded_lib/` 中的文件永远不修改、不删除
2. **按需复制**：只复制工程实际用到的外设驱动文件，不全量拷贝
3. **路径自包含**：工程内所有路径引用必须指向工程自身目录，禁止引用 `embedded_lib/` 绝对路径
4. **编译器一致**：8051 用 Keil C51，ARM 用 Keil MDK 或 GCC ARM，不可混用
5. **注释英文**：代码注释统一使用英文（避免中文编码乱码）

---

## 4. 工程目录模板

### 4.1 8051 系列工程模板

```
embedded_item/{project_name}/
├── User/
│   ├── main.c
│   ├── main.h
│   ├── interrupt.c               # 中断服务程序
│   └── config.h                  # 芯片配置宏（时钟、IO 默认值）
├── App/
│   ├── app_key.c                 # 按键应用
│   ├── app_led.c                 # LED 应用
│   └── app_motor.c               # 电机应用（如有）
├── Drivers/
│   ├── drv_gpio.c / .h
│   ├── drv_uart.c / .h
│   ├── drv_timer.c / .h
│   └── drv_adc.c / .h
├── Libraries/                    # 从 embedded_lib/ 复制
│   ├── Include/
│   │   ├── CMS8S6990.h
│   │   └── stdint_c51.h
│   └── Startup/
│       └── STARTUP.A51
├── Output/                       # 编译输出
├── CMS8S6990.uvprojx             # Keil 工程文件
└── README.md
```

### 4.2 ARM 系列工程模板

```
embedded_item/{project_name}/
├── Core/
│   ├── Inc/
│   │   ├── main.h
│   │   ├── stm32fxxx_it.h        # CMS32M 中断头文件
│   │   └── cmsis_compiler.h
│   └── Src/
│       ├── main.c
│       ├── system_CMS32M67xx.c   # 系统初始化
│       └── irq_handler.c         # 中断处理
├── App/
│   ├── app_motor.c               # 电机 FOC 应用
│   ├── app_adc.c                 # ADC 采样应用
│   └── app_comm.c                # 通信应用
├── Drivers/
│   ├── drv_gpio.c / .h
│   ├── drv_uart.c / .h
│   ├── drv_adc.c / .h
│   └── drv_pwm.c / .h
├── Libraries/                    # 从 embedded_lib/ 复制
│   ├── CMSIS/
│   │   ├── Include/              # core_cm0.h
│   │   └── Device/CMS32M67xx/
│   │       ├── Include/          # CMS32M67xx.h
│   │       └── Source/ARM/       # startup .s
│   └── DriverLib/
│       ├── inc/                  # cms32m67xx_xxx.h
│       └── src/                  # cms32m67xx_xxx.c
├── LinkerScripts/
│   └── CMS32M67xx_flash.ld       # GCC 链接脚本
├── Makefile                      # 或 .uvprojx (Keil)
└── README.md
```

---

## 5. 构建系统

### 5.1 8051 (Keil C51)

8051 系列推荐直接使用 **Keil uVision** 工程文件（`.uvprojx`），不强制要求 Makefile。

若需要 Makefile 构建，使用 Keil 的 `UV4` 命令行：

```makefile
# Keil C51 命令行编译
CC = C51
AS = A51
LD = LX51

TARGET = Output/project.hex

CFLAGS = DB OE NS
AFLAGS =

SRCS = User/main.c Drivers/drv_gpio.c Drivers/drv_uart.c
ASMS = Libraries/Startup/STARTUP.A51

$(TARGET): $(SRCS) $(ASMS)
	$(CC) $(CFLAGS) $^
	@echo "Build complete: $@"
```

### 5.2 ARM (GCC ARM / Makefile)

ARM 系列使用标准 GCC ARM 交叉编译工具链：

```makefile
# Toolchain
PREFIX = arm-none-eabi-
CC = $(PREFIX)gcc
AS = $(PREFIX)gcc -x assembler-with-cpp
LD = $(PREFIX)gcc
OBJCOPY = $(PREFIX)objcopy
SIZE = $(PREFIX)size

# Target
TARGET = output/cms32m6710_project
BUILD_DIR = build

# MCU specific
CPU = -mcpu=cortex-m0
FPU =
FLOAT-ABI = -mfloat-abi=soft
MCU = $(CPU) -mthumb $(FPU) $(FLOAT-ABI)

# Defines
C_DEFS = -DCMS32M67xx

# Include paths (all internal)
C_INCLUDES = \
	-ILibraries/CMSIS/Include \
	-ILibraries/CMSIS/Device/CMS32M67xx/Include \
	-ILibraries/DriverLib/inc \
	-ICore/Inc

# Sources
C_SOURCES = \
	Core/Src/main.c \
	Core/Src/system_CMS32M67xx.c \
	Core/Src/irq_handler.c \
	Libraries/DriverLib/src/cms32m67xx_gpio.c \
	Libraries/DriverLib/src/cms32m67xx_uart.c \
	Libraries/DriverLib/src/cms32m67xx_timer.c

ASM_SOURCES = \
	Libraries/CMSIS/Device/CMS32M67xx/Source/ARM/startup_CMS32M67xx.s

# Compiler flags
CFLAGS = $(MCU) $(C_DEFS) $(C_INCLUDES) -Os -Wall -ffunction-sections -fdata-sections
LDFLAGS = $(MCU) -specs=nano.specs -TLinkerScripts/CMS32M67xx_flash.ld \
          -Wl,--gc-sections -Wl,-Map=$(BUILD_DIR)/$(TARGET).map

# Build rules
all: $(BUILD_DIR)/$(TARGET).elf $(BUILD_DIR)/$(TARGET).hex

$(BUILD_DIR)/$(TARGET).elf: $(OBJECTS)
	$(LD) $(LDFLAGS) -o $@ $^
	$(SIZE) $@

$(BUILD_DIR)/%.o: %.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD_DIR)/%.o: %.s | $(BUILD_DIR)
	$(AS) $(MCU) -c $< -o $@

flash:
	openocd -f interface/cms-dap.cfg -f target/cms32m.cfg \
	        -c "program $(BUILD_DIR)/$(TARGET).elf verify reset exit"
```

---

## 6. CMS 芯片开发注意事项

### 6.1 时钟系统

| 系列 | 时钟源 | 最大主频 | 配置方式 |
|------|--------|---------|----------|
| CMS8S | IHRC (内部高速) / EHC (外部) | 48 MHz | CLKCON 寄存器 |
| CMS32M67xx | HSI / HSE / PLL | 48 MHz | DriverLib: SYSCTL_clockInit() |
| CMS32L052 | MSI / HSE / PLL | 32 MHz | DriverLib: SYSCTL_clockInit() |

### 6.2 GPIO 配置要点

- **8051 系列**：P0-P3 传统端口，通过 PxM0/PxM1 寄存器配置推挽/开漏/上拉
- **ARM 系列**：AFIO + GPIO 外设，DriverLib 接口类似 STM32 HAL

### 6.3 中断系统

- **8051 系列**：4 个优先级（IP / IPH），中断号在 `CMS8S6990.h` 中定义
- **ARM 系列**：NVIC，支持 2 级优先级（Cortex-M0），中断向量表在启动文件中

### 6.4 电机控制 (CMS32M67xx 专用)

CMS32M67xx 内置 MCPWM（电机控制 PWM）模块，支持：
- 三相互补 PWM 输出
- ADC 触发同步
- 死区时间配置
- 故障保护输入（Brake）
- 适配 FOC / 方波 / 梯形波控制算法

---

## 7. 烧录调试工具

| 工具 | 支持系列 | 接口 | 备注 |
|------|---------|------|------|
| **CMS DAPLink** | ARM 系列 | SWD | CMS 官方调试器 |
| **CMS ICE** | 8051 系列 | ISP / SWD | CMS 8051 专用 |
| **OpenOCD** | ARM 系列 | SWD | 需配置 CMS 适配脚 |
| **Keil ULINK** | 全系列 | SWD / JTAG | 通用，需 CMS pack |
| **J-Link** | ARM 系列 | SWD | 需确认芯片支持 |

---

## 8. 常见开发问题

### Q1: Keil 找不到 CMS 芯片型号
**解决**：安装 CMS Device Family Pack（DFP）。从 CMS 官网下载 `.pack` 文件，在 Keil 中 `Pack Installer → File → Import` 导入。

### Q2: 8051 程序无法启动
**解决**：检查 STARTUP.A51 是否正确添加到工程、堆栈指针（SP）初始化、看门狗配置（部分 CMS8S 默认开启看门狗）。

### Q3: ARM 程序 HardFault
**解决**：
1. 检查中断向量表地址（VECT_TAB）
2. 检查链接脚本中 FLASH/RAM 地址与芯片手册一致
3. 使用 `objdump -d` 反汇编确认 Reset_Handler 入口

### Q4: ADC 采样值异常
**解决**：
1. 确认 ADC 时钟分频设置（采样时间不能太短）
2. 检查参考电压源（内部 VDD / 外部 VREF）
3. 确认 GPIO 复用功能正确配置

---

## 9. 经验沉淀规则

每次完成 CMS 相关开发任务后：
1. 将新的寄存器配置经验写入 `memory/` 目录对应的文件
2. 标签使用 `#cms-embedded` `#cms8s` / `#cms32m` / `#cms32l`
3. 涉及到 SDK 库文件更新，提醒用户同步到 `embedded_lib/cms-*/` 目录

---

## 10. 变更记录

| 版本 | 日期 | 主要改动 |
|------|------|---------|
| 1.0 | 2026-05-11 | 初始版本，覆盖 CMS8S/80F/79F (8051) 和 CMS32M/CMS32L (ARM) 全系列 |
