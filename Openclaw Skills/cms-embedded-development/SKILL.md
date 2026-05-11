---
name: cms-embedded-development
description: |
  CMS（中微半导体）嵌入式代码自主化工作流
  适用于 CMS32F/CMS32M 系列（ARM Cortex-M0）及 CMS8S/CMS80F/CMS79F（8051 内核）
  流程：用户需求 → 芯片判定 → 框架检测 → 结构化拆解 → 知识库检索 → 代码生成 → 审查测试 → 交付 + 经验沉淀
---

# CMS (中微半导体) Embedded Development Workflow

## 1. 角色定位与信息流

| 步骤 | 执行者     | 目的                                         | 关键工具 / 指令                          | 输出物                |
|------|-----------|----------------------------------------------|------------------------------------------|-----------------------|
| 0    | main      | 芯片系列判定 + SDK 路径确认                    | read + grep on project files             | Chip & Env Decision   |
| 1    | main      | 拆解用户需求，生成结构化任务单 + 需求文档       | -                                        | Task Brief            |
| 2    | clerk     | 从知识库检索 CMS 相关经验与寄存器配置           | memory_search + wiki_search              | Raw Experiences       |
| 3    | clerk     | 将原始经验转化为结构化摘要                     | code_execution                           | Structured Summary    |
| 4    | coder     | 基于摘要生成完整、可编译的代码工程             | sessions_send → coder                    | Full Project Code     |
| 5    | evaluator | 代码审查、静态分析、编译验证                   | sessions_send → evaluator + code_execution | Review Report         |
| 6    | main      | 最终交付 + 记录新经验                         | write + memory_learn                     | Delivered + Knowledge |

---

## 2. 芯片系列与内核架构判定

### 2.1 芯片系列速查

#### ARM Cortex-M0 系列（CMS32 SDK 已集成）

| 系列 | 用途 | 特色外设 |
|------|------|----------|
| **CMS32F030** | 通用控制 | ADC, EPWM, I2C, SPI, UART, Timer |
| **CMS32F033** | 通用控制 | ACMP, ADC1, CCP, CRC, EPWM, OPA, PGA, HWDIV |
| **CMS32F035** | 通用控制 + 电机 | ADC0, ADCB, EPWM, OPA, PGA, CRC, HWDIV |
| **CMS32M53xx** | 电机控制 | ADC1, EPWM, OPA, CRC, HWDIV (无 PGA/ADC0) |
| **CMS32M55xx** | 电机控制 | ADC0, ADC1, EPWM, OPA, PGA, CRC, HWDIV |
| **CMS32M57xx** | 电机控制 | ADC0, ADCB, EPWM, OPA, PGA, CRC, HWDIV |
| **CMS32MEBIKE** | 电动自行车专用 | 电机控制专用外设 |

#### 8051 系列（需额外 SDK）

| 系列 | 编译器 | 用途 |
|------|--------|------|
| **CMS8S** | Keil C51 | 通用控制、消费电子 |
| **CMS80F** | Keil C51 | 高性能 8 位控制 |
| **CMS79F** | Keil C51 | 触摸按键、小家电 |

### 2.2 芯片判定流程

```
IF 工程目录存在 → 执行以下检测：
  1. 在 Makefile / .uvprojx 中查找 DEVICE 或 MCU 声明
  2. 检查 Device/ 下的头文件名
  3. 检查启动文件名
  4. 以上均未命中 → 用户必须提供芯片型号
ELSE 无工程目录 → 用户必须提供芯片型号
```

### 2.3 主管输出格式

```yaml
chip_decision:
  chip_family: CMS32F030 | CMS32F033 | CMS32F035 | CMS32M53xx | CMS32M55xx | CMS32M57xx | CMS32MEBIKE
  core: cortex-m0
  sdk_version: "Cmsemicon.CMS32-Series.1.1.3"
  driver_module: "Driver/CMS32M55xx"       # 对应 SDK 中的驱动目录
  device_module: "Device/CMS32M55xx"       # 对应 SDK 中的设备目录
  available_peripherals: [acmp, adc0, adc1, ccp, crc, epwm, fmc, gpio, hwdiv, i2c, opa, pga, ssp, system, timer, uart, wdt, wwdt]
  flash_algo: "Flash/CMS32M55xx.FLM"       # Keil 烧录算法
  reason: "检测到 Device=CMS32M55xx，确认为 ARM Cortex-M0 电机控制系列"
  detection_method: "directory_scan" | "user_specified" | "prompt_required"
```

### 2.4 各芯片外设差异速查

| 外设 | F030 | F033 | F035 | M53xx | M55xx | M57xx |
|------|------|------|------|-------|-------|-------|
| ADC0 | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ |
| ADC1 | ❌ | ✅ | ❌ | ✅ | ✅ | ❌ |
| ADCB | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| ACMP | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| OPA | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| PGA | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ |
| EPWM | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| CCP | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| CRC | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| HWDIV | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| SSP (SPI) | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |

---

## 3. 项目创建工作区规范

### 3.1 目录定义

| 目录 | 路径 | 用途 | 权限 |
|------|------|------|------|
| **库文件目录** | `/home/whites/embedded_lib/` | CMS32 SDK + STM32 库 | **只读**，禁止修改/引用 |
| **工程项目目录** | `/home/whites/embedded_item/` | 新建工程 | 读写 |

### 3.2 CMS32 SDK 实际目录结构

```
embedded_lib/Cmsemicon.CMS32-Series.1.1.3/
├── Device/                          # 芯片设备支持
│   ├── CMS32F030/
│   │   ├── Include/
│   │   │   ├── CMS32F030.h          # 寄存器定义（核心）
│   │   │   └── system_CMS32F030.h   # 系统初始化头文件
│   │   └── Source/
│   │       ├── ARM/
│   │       │   └── startup_CMS32F030.s  # 启动文件 (Keil MDK)
│   │       └── system_CMS32F030.c       # 系统时钟初始化
│   ├── CMS32F033/
│   ├── CMS32F035/
│   ├── CMS32M53xx/
│   ├── CMS32M55xx/
│   ├── CMS32M57xx/
│   └── CMS32MEBIKE/
├── Driver/                          # 外设驱动库
│   ├── CMS32F030/
│   │   ├── inc/
│   │   │   ├── adc.h, epwm.h, gpio.h, i2c.h ...
│   │   │   └── core_cm0.h           # CMSIS 核心
│   │   └── src/
│   │       ├── adc.c, epwm.c, gpio.c, i2c.c ...
│   │       └── retarget.c           # printf 重定向
│   ├── CMS32F033/
│   ├── CMS32F035/
│   ├── CMS32M53xx/
│   ├── CMS32M55xx/                  # 21 个外设模块
│   ├── CMS32M57xx/
│   └── ...（每芯片独立驱动，外设组合不同）
├── Examples/                        # 官方示例（每芯片一套）
│   └── CMS32M55xx/
│       ├── ACMP, ADC0, ADC1, CCP, CRC, EPWM, FMC, GPIO,
│       │   HWDIV, I2C, OPA, PGA, SPI, STB, SystemClkOut,
│       │   Systick, Timer, UART, WDT, WWDT
├── Documents/                       # 文档
│   └── dui0497a_cortex_m0_r0p0_generic_ug.pdf  # Cortex-M0 用户指南
├── Flash/                           # Keil 烧录算法 (.FLM)
│   ├── CMS32F030.FLM
│   ├── CMS32M53xx.FLM
│   ├── CMS32M55xx.FLM
│   └── ...
└── SVD/                             # SVD 文件（调试用）
```

### 3.3 创建新工程流程（铁律）

```
1. 在 /home/whites/embedded_item/ 下创建工程目录
   mkdir -p /home/whites/embedded_item/{project_name}/

2. 从 embedded_lib/ 按需复制到工程内（禁止引用 embedded_lib/ 路径）
   SDK_DIR=/home/whites/embedded_lib/Cmsemicon.CMS32-Series.1.1.3
   CHIP=CMS32M55xx

   # 复制设备支持
   mkdir -p Libraries/Device/Include Libraries/Device/Source/ARM
   cp $SDK_DIR/Device/$CHIP/Include/*.h       Libraries/Device/Include/
   cp $SDK_DIR/Device/$CHIP/Source/ARM/*.s    Libraries/Device/Source/ARM/
   cp $SDK_DIR/Device/$CHIP/Source/system_*.c Libraries/Device/Source/

   # 复制驱动库（按需）
   mkdir -p Libraries/Driver/inc Libraries/Driver/src
   cp $SDK_DIR/Driver/$CHIP/inc/*.h           Libraries/Driver/inc/
   cp $SDK_DIR/Driver/$CHIP/src/gpio.c        Libraries/Driver/src/
   cp $SDK_DIR/Driver/$CHIP/src/uart.c        Libraries/Driver/src/
   # ... 只复制实际用到的外设

   # 复制烧录算法
   cp $SDK_DIR/Flash/$CHIP.FLM               LinkerScripts/

3. 编写业务代码（main.c, app/, drivers/ 等）

4. Makefile / IDE 中所有 -I 路径指向工程内 Libraries/ 目录
   # ✅ -ILibraries/Driver/inc
   # ✅ -ILibraries/Device/Include
   # ❌ -I/home/whites/embedded_lib/Cmsemicon.CMS32-Series.1.1.3/Driver/...

5. 编译验证
```

### 3.4 铁律

1. **库文件只读**：`/home/whites/embedded_lib/` 中的文件永远不修改、不删除、不引用
2. **按需复制**：只复制工程实际用到的外设驱动，不全量拷贝
3. **路径自包含**：工程内所有 `-I`、`-L`、源文件路径指向工程自身目录
4. **注释英文**：代码注释统一使用英文

---

## 4. 工程目录模板

### 4.1 CMS32M55xx 工程模板

```
embedded_item/{project_name}/
├── Core/
│   ├── Inc/
│   │   ├── main.h
│   │   └── irq_handler.h
│   └── Src/
│       ├── main.c
│       └── irq_handler.c
├── App/
│   ├── app_motor.c               # 电机应用
│   ├── app_adc.c                 # ADC 应用
│   └── app_comm.c                # 通信应用
├── Drivers/
│   ├── drv_gpio.c / .h
│   ├── drv_uart.c / .h
│   └── drv_epwm.c / .h
├── Libraries/                    # 从 embedded_lib/ 复制（只读源）
│   ├── Device/
│   │   ├── Include/
│   │   │   ├── CMS32M55xx.h
│   │   │   └── system_CMS32M55xx.h
│   │   └── Source/
│   │       ├── ARM/
│   │       │   └── startup_CMS32M55xx.s
│   │       └── system_CMS32M55xx.c
│   └── Driver/
│       ├── inc/
│       │   ├── core_cm0.h        # CMSIS 核心
│       │   ├── core_cmFunc.h
│       │   ├── core_cmInstr.h
│       │   ├── gpio.h
│       │   ├── uart.h
│       │   ├── timer.h
│       │   ├── adc0.h
│       │   ├── adc1.h
│       │   ├── epwm.h
│       │   ├── acmp.h
│       │   ├── opa.h
│       │   ├── pga.h
│       │   ├── i2c.h
│       │   ├── ssp.h
│       │   ├── ccp.h
│       │   ├── crc.h
│       │   ├── hwdiv.h
│       │   ├── fmc.h
│       │   ├── system.h
│       │   ├── wdt.h
│       │   └── wwdt.h
│       └── src/                  # 按需复制 .c 文件
├── LinkerScripts/
│   └── CMS32M55xx.FLM            # Keil 烧录算法
├── Makefile                      # 或 .uvprojx (Keil)
└── README.md
```

### 4.2 关键文件说明

| 文件 | 来源 SDK 路径 | 作用 |
|------|-------------|------|
| `CMS32M55xx.h` | `Device/CMS32M55xx/Include/` | 寄存器地址映射，中断号定义 |
| `system_CMS32M55xx.c` | `Device/CMS32M55xx/Source/` | SystemInit()，时钟配置 |
| `startup_CMS32M55xx.s` | `Device/CMS32M55xx/Source/ARM/` | 中断向量表，Reset_Handler |
| `core_cm0.h` | `Driver/CMS32M55xx/inc/` | CMSIS Cortex-M0 核心函数 |
| `gpio.h / gpio.c` | `Driver/CMS32M55xx/inc/ src/` | GPIO 外设驱动 |
| `epwm.h / epwm.c` | `Driver/CMS32M55xx/inc/ src/` | 增强型 PWM 驱动（电机控制核心） |

---

## 5. 构建系统

### 5.1 ARM (GCC ARM / Makefile)

```makefile
# Toolchain
PREFIX = arm-none-eabi-
CC = $(PREFIX)gcc
AS = $(PREFIX)gcc -x assembler-with-cpp
LD = $(PREFIX)gcc
OBJCOPY = $(PREFIX)objcopy
SIZE = $(PREFIX)size

# Target
CHIP = CMS32M55xx
TARGET = output/$(CHIP)_project
BUILD_DIR = build

# MCU
CPU = -mcpu=cortex-m0
MCU = $(CPU) -mthumb -mfloat-abi=soft

# Defines
C_DEFS = -D$(CHIP)

# Include paths (ALL internal — no embedded_lib/ reference)
C_INCLUDES = \
	-ILibraries/Driver/inc \
	-ILibraries/Device/Include \
	-ICore/Inc

# Sources
C_SOURCES = \
	Core/Src/main.c \
	Core/Src/irq_handler.c \
	Libraries/Device/Source/system_$(CHIP).c \
	Libraries/Driver/src/gpio.c \
	Libraries/Driver/src/uart.c \
	Libraries/Driver/src/epwm.c \
	Libraries/Driver/src/timer.c \
	Libraries/Driver/src/adc0.c

ASM_SOURCES = \
	Libraries/Device/Source/ARM/startup_$(CHIP).s

# Flags
CFLAGS = $(MCU) $(C_DEFS) $(C_INCLUDES) -Os -Wall -ffunction-sections -fdata-sections
LDFLAGS = $(MCU) -specs=nano.specs -TLinkerScripts/$(CHIP).ld \
          -Wl,--gc-sections -Wl,-Map=$(BUILD_DIR)/$(TARGET).map

# Build
all: $(BUILD_DIR)/$(TARGET).elf

$(BUILD_DIR)/$(TARGET).elf: $(OBJECTS)
	$(LD) $(LDFLAGS) -o $@ $^
	$(SIZE) $@

$(BUILD_DIR)/%.o: %.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD_DIR)/%.o: $(ASM_SOURCES) | $(BUILD_DIR)
	$(AS) $(MCU) -c $< -o $@

flash:
	openocd -f interface/cms-dap.cfg -f target/cms32m.cfg \
	        -c "program $(BUILD_DIR)/$(TARGET).elf verify reset exit"
```

### 5.2 Keil MDK

使用 `.uvprojx` 工程文件，关键配置：
- **Target → Device**：选择对应 CMS32 型号
- **C/C++ → Include Paths**：指向工程内 Libraries/
- **Linker → Misc**：确保 Scatter File 路径正确
- **Flash → Programming Algorithm**：使用 `LinkerScripts/CHIP.FLM`

---

## 6. CMS32 开发注意事项

### 6.1 时钟系统

CMS32 系列使用 `system_xxx.c` 中的 `SystemInit()` 配置时钟，默认配置通常在芯片头文件的宏中定义。编译前需确认：
- `HSI` 内部高速时钟频率
- `SYSCLK` 目标主频
- 各总线分频系数（AHB / APB）

### 6.2 GPIO 配置

- GPIO 驱动通过 `Driver/inc/gpio.h` 提供统一接口
- 配置模式：推挽输出、开漏输出、上拉输入、模拟输入
- 复用功能通过 AF 寄存器配置

### 6.3 中断系统

- Cortex-M0 核心，2 级优先级
- 中断向量表在 `startup_CMS32xxx.s` 中定义
- 中断号在 `CMS32xxx.h` 中以枚举形式定义（`IRQn_Type`）
- NVIC 优先级位数：2-bit（0-3 优先级）

### 6.4 电机控制 (EPWM)

CMS32M 系列的 EPWM（增强型 PWM）是电机控制核心外设：
- 互补 PWM 输出（上下桥臂）
- 死区时间可编程
- ADC 触发同步（电流采样时机）
- 故障保护输入（Brake / 过流保护）
- 支持 FOC / 方波 / 梯形波控制

### 6.5 各芯片驱动差异

> ⚠️ 每个 CMS32 型号的驱动库**独立存在**，外设头文件名不带芯片前缀
> 例如 `CMS32M55xx/inc/gpio.h` 和 `CMS32F030/inc/gpio.h` 是不同文件
> 必须复制**目标芯片对应**的驱动目录，不可混用

---

## 7. 烧录调试工具

| 工具 | 接口 | 配置要点 |
|------|------|----------|
| **CMS DAPLink** | SWD | CMS 官方调试器 |
| **Keil ULINK** | SWD | 使用 `Flash/CHIP.FLM` 烧录算法 |
| **J-Link** | SWD | 需在 J-Link 中添加 CMS 芯片支持 |
| **OpenOCD** | SWD | 需配置 CMS 适配脚 |

### Keil 烧录算法配置

将 `embedded_lib/Cmsemicon.CMS32-Series.1.1.3/Flash/CHIP.FLM` 复制到工程 `LinkerScripts/` 目录，在 Keil 中：
- **Options → Debug → Settings → Flash Download**
- **Programming Algorithm** → Add → 选择 `CHIP.FLM`

---

## 8. 官方示例参考路径

SDK 中每个芯片都有完整的外设示例：

```
embedded_lib/Cmsemicon.CMS32-Series.1.1.3/Examples/CMS32M55xx/
├── ACMP/          # 模拟比较器
├── ADC0/          # ADC0 采样
├── ADC1/          # ADC1 采样
├── CCP/           # 捕获/比较/PWM
├── CRC/           # CRC 计算
├── EPWM/          # 增强型 PWM（电机控制）
├── FMC/           # Flash 存储控制
├── GPIO/          # GPIO 输入输出
├── HWDIV/         # 硬件除法器
├── I2C/           # I2C 通信
├── OPA/           # 运算放大器
├── PGA/           # 可编程增益放大器
├── SPI/           # SPI 通信
├── STB/           # 系统定时器
├── SystemClkOut/  # 时钟输出
├── Systick/       # SysTick 定时器
├── Timer/         # 通用定时器
├── UART/          # UART 通信
├── WDT/           # 看门狗
└── WWDT/          # 窗口看门狗
```

> 示例代码是最佳参考，但同样需复制到工程内修改，不可直接在 embedded_lib/ 下编译。

---

## 9. 经验沉淀规则

每次完成 CMS 相关开发任务后：
1. 将新的寄存器配置经验写入 `memory/` 目录对应的文件
2. 标签使用 `#cms-embedded` `#cms32f` `#cms32m` `#cms32mebike`
3. 涉及到 SDK 库文件更新，提醒用户同步到 `embedded_lib/` 目录

---

## 10. 变更记录

| 版本 | 日期 | 主要改动 |
|------|------|---------|
| 1.0 | 2026-05-11 | 初始版本 |
| 2.0 | 2026-05-11 | 根据实际 SDK (Cmsemicon.CMS32-Series.1.1.3) 重写：修正芯片型号（F030/F033/F035/M53xx/M55xx/M57xx/MEBIKE），更新目录结构、驱动外设差异、工程模板、构建脚本 |
