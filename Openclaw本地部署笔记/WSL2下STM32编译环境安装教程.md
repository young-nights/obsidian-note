---
title: WSL2 下 STM32 编译环境安装教程
type: tutorial
tags: [stm32, wsl2, arm-gcc, hal, spl, rt-thread, embedded, build]
created: 2026-05-10
updated: 2026-05-10
---

# WSL2 下 STM32 编译环境安装教程

> 在 Windows 11 + WSL2 Ubuntu 环境中搭建 STM32 编译工具链，支持标准库 (SPL)、HAL 库、RT-Thread 三种开发模式。

## 1. 环境概览

| 项目 | 说明 |
|------|------|
| 宿主系统 | Windows 11 |
| 虚拟化 | WSL2 (Ubuntu 24.04) |
| 目标芯片 | STM32F1/F4/F7/H7/G0 系列 |
| 支持模式 | 标准库 (SPL)、HAL 库、RT-Thread (Nano/Standard) |

## 2. 通用工具链安装

三个开发模式的共同基础，只需安装一次。

### 2.1 ARM 交叉编译器

```bash
sudo apt update
sudo apt install -y gcc-arm-none-eabi
```

验证安装：
```bash
arm-none-eabi-gcc --version
# 预期输出：arm-none-eabi-gcc (15:13.2.rel1-6) 13.2.1 ...
```

### 2.2 构建工具

```bash
sudo apt install -y make cmake
```

### 2.3 Git

```bash
sudo apt install -y git
```

### 2.4 烧录工具（可选）

如果需要通过 ST-Link 烧录固件：

```bash
# OpenOCD（支持 ST-Link/J-Link 调试器）
sudo apt install -y openocd

# ST-Link 命令行工具
sudo apt install -y stlink-tools
```

验证：
```bash
openocd --version
st-info --version
```

> **注意**：WSL2 中 USB 设备直通需要安装 [usbipd-win](https://github.com/dorssel/usbipd-win)，ST-Link 连接步骤见 [附录 A](#附录-a-wsl2-usb-设备直通)。

---

## 3. 标准库 (SPL) 环境

适用于 STM32F1 系列为主。

### 3.1 下载标准外设库

```bash
# 方法一：从 ST GitHub 获取（以 F1 为例）
cd ~
git clone https://github.com/STMicroelectronics/STM32F10x_StdPeriph_Lib.git

# 方法二：手动下载
# 访问 https://www.st.com/en/embedded-software/stm32-stdperiph-lib.html
# 下载后解压到 ~/STM32F10x_StdPeriph_Lib_V3.5.0/
```

### 3.2 目录结构

```
~/STM32F10x_StdPeriph_Lib/
├── Libraries/
│   ├── CMSIS/                          # ARM CMSIS 核心文件
│   │   ├── CM3/
│   │   │   ├── DeviceSupport/ST/STM32F10x/
│   │   │   │   ├── startup/            # 启动文件 (startup_stm32f10x_hd.s)
│   │   │   │   ├── system_stm32f10x.c
│   │   │   │   └── stm32f10x.h
│   │   │   └── CoreSupport/            # CMSIS 核心 (core_cm3.h)
│   └── STM32F10x_StdPeriph_Driver/     # 标准外设驱动
│       ├── inc/                        # 头文件 (stm32f10x_gpio.h ...)
│       └── src/                        # 源文件 (stm32f10x_gpio.c ...)
├── Project/
│   └── STM32F10x_StdPeriph_Template/   # 官方模板工程
└── Utilities/
```

### 3.3 最小 Makefile 模板

```makefile
# Makefile for STM32F1 + SPL
PROJECT = my_project
CHIP    = STM32F103C8

# 工具链
CC      = arm-none-eabi-gcc
OBJCOPY = arm-none-eabi-objcopy
SIZE    = arm-none-eabi-size

# 路径
SPL_DIR    = ~/STM32F10x_StdPeriph_Lib/Libraries/STM32F10x_StdPeriph_Driver
CMSIS_DIR  = ~/STM32F10x_StdPeriph_Lib/Libraries/CMSIS

# 编译参数
CFLAGS  = -mcpu=cortex-m3 -mthumb -Os -Wall
CFLAGS += -DSTM32F10X_MD -DUSE_STDPERIPH_DRIVER
CFLAGS += -I$(SPL_DIR)/inc -I$(CMSIS_DIR)/CM3/DeviceSupport/ST/STM32F10x -I$(CMSIS_DIR)/CM3/CoreSupport

# 源文件
SRCS  = main.c system_stm32f10x.c
SRCS += $(SPL_DIR)/src/stm32f10x_gpio.c
SRCS += $(SPL_DIR)/src/stm32f10x_rcc.c
# 添加需要的外设驱动...

# 启动文件
STARTUP = $(CMSIS_DIR)/CM3/DeviceSupport/ST/STM32F10x/startup/gcc_ride7/startup_stm32f10x_md.s

# 链接脚本
LDSCRIPT = stm32f103c8_flash.ld

all: $(PROJECT).elf $(PROJECT).bin

$(PROJECT).elf: $(SRCS) $(STARTUP)
	$(CC) $(CFLAGS) -T$(LDSCRIPT) -o $@ $^ -lc -lnosys

$(PROJECT).bin: $(PROJECT).elf
	$(OBJCOPY) -O binary $< $@
	$(SIZE) $<

flash: $(PROJECT).bin
	openocd -f interface/stlink.cfg -f target/stm32f1x.cfg -c "program $< verify reset exit"

clean:
	rm -f $(PROJECT).elf $(PROJECT).bin
```

---

## 4. HAL 库环境

适用于 STM32F4/F7/H7/G0 等系列。

### 4.1 下载 HAL 固件包

```bash
# 以 STM32F4 为例
cd ~
git clone https://github.com/STMicroelectronics/STM32CubeF4.git

# 其他系列：
# STM32F7: git clone https://github.com/STMicroelectronics/STM32CubeF7.git
# STM32H7: git clone https://github.com/STMicroelectronics/STM32CubeH7.git
# STM32G0: git clone https://github.com/STMicroelectronics/STM32CubeG0.git
```

### 4.2 目录结构

```
~/STM32CubeF4/
├── Drivers/
│   ├── CMSIS/                          # CMSIS 核心 + DSP
│   │   ├── Include/
│   │   ├── Device/ST/STM32F4xx/
│   │   │   ├── Include/                # stm32f4xx.h, system_stm32f4xx.h
│   │   │   └── Source/Templates/        # system_stm32f4xx.c, startup .s
│   │   └── DSP_Lib/
│   └── STM32F4xx_HAL_Driver/           # HAL 驱动
│       ├── Inc/                        # stm32f4xx_hal.h, stm32f4xx_hal_gpio.h ...
│       └── Src/                        # stm32f4xx_hal.c, stm32f4xx_hal_gpio.c ...
├── Middlewares/                        # 第三方中间件（LwIP, FatFs, USB...）
├── Projects/                           # 官方示例工程
└── Utilities/
```

### 4.3 CubeMX CLI（可选但推荐）

```bash
# 安装 STM32CubeMX（Linux 版）
# 1. 从 https://www.st.com/en/development-tools/stm32cubeclt.html 下载
# 2. 解压安装
cd ~/Downloads
unzip en.stm32cubeclt_lnx_v1-17-0.zip
./st-stm32cubeclt_1.17.0_21046_20241126_1703_amd64.sh

# 添加到 PATH
echo 'export PATH="$HOME/STMicroelectronics/STM32CubeCLT/1.17.0/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 验证
stm32cubeclt-cli --version
```

### 4.4 最小 Makefile 模板

```makefile
# Makefile for STM32F4 + HAL
PROJECT = my_project
CHIP    = STM32F407xx

CC      = arm-none-eabi-gcc
OBJCOPY = arm-none-eabi-objcopy
SIZE    = arm-none-eabi-size

# 路径
HAL_DIR   = ~/STM32CubeF4/Drivers/STM32F4xx_HAL_Driver
CMSIS_DIR = ~/STM32CubeF4/Drivers/CMSIS

CFLAGS  = -mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16 -Os -Wall
CFLAGS += -D$(CHIP) -DUSE_HAL_DRIVER
CFLAGS += -I./Core/Inc
CFLAGS += -I$(HAL_DIR)/Inc
CFLAGS += -I$(CMSIS_DIR)/Device/ST/STM32F4xx/Include
CFLAGS += -I$(CMSIS_DIR)/Include

SRCS  = Core/Src/main.c Core/Src/stm32f4xx_it.c Core/Src/stm32f4xx_hal_msp.c
SRCS += $(CMSIS_DIR)/Device/ST/STM32F4xx/Source/Templates/system_stm32f4xx.c
SRCS += $(HAL_DIR)/Src/stm32f4xx_hal.c
SRCS += $(HAL_DIR)/Src/stm32f4xx_hal_rcc.c
SRCS += $(HAL_DIR)/Src/stm32f4xx_hal_gpio.c
SRCS += $(HAL_DIR)/Src/stm32f4xx_hal_cortex.c
# CubeMX 生成的代码会自动列出所有需要的 HAL 源文件

STARTUP  = $(CMSIS_DIR)/Device/ST/STM32F4xx/Source/Templates/gcc/startup_stm32f407xx.s
LDSCRIPT = STM32F407IG_FLASH.ld

all: $(PROJECT).elf $(PROJECT).bin

$(PROJECT).elf: $(SRCS) $(STARTUP)
	$(CC) $(CFLAGS) -T$(LDSCRIPT) -o $@ $^ -lc -lnosys -Wl,--gc-sections

$(PROJECT).bin: $(PROJECT).elf
	$(OBJCOPY) -O binary $< $@
	$(SIZE) $<

flash: $(PROJECT).bin
	openocd -f interface/stlink.cfg -f target/stm32f4x.cfg -c "program $< verify reset exit"

clean:
	rm -f $(PROJECT).elf $(PROJECT).bin
```

---

## 5. RT-Thread 环境

### 5.1 RT-Thread Standard（标准版）

```bash
# 1. 安装 SCons 构建工具
sudo apt install python3-pip
# Ubuntu 24.04 的 Python 3.12+ 启用 PEP 668 保护，pip install 需加 --break-system-packages
pip3 install scons --break-system-packages
scons --version    # 验证

# 2. 克隆 RT-Thread 源码
cd ~
git clone https://github.com/RT-Thread/rt-thread.git
cd rt-thread
git checkout v5.2.0    # 切换到稳定版

# 3. 选择 BSP（以 STM32F407-Discovery 为例）
cd bsp/stm32/stm32f407-st-discovery/

# 4. 配置（menuconfig）
pkgs --upgrade          # 更新软件包（如有）
scons --menuconfig      # 图形化配置 RT-Thread 组件

# 5. 编译
scons                  # 直接 GCC 编译

# 或生成 Keil 工程
scons --target=mdk5
```

**BSP 目录结构**：
```
rt-thread/bsp/stm32/stm32f407-st-discovery/
├── applications/
│   └── main.c              # 入口
├── drivers/
│   ├── board.c             # 系统时钟 + 外设初始化
│   ├── board.h
│   ├── drv_usart.c
│   └── ...
├── CubeMX_Config/           # CubeMX .ioc 文件
├── Kconfig                  # menuconfig 配置
├── SConstruct               # SCons 入口
├── SConscript               # 源文件声明
├── rtconfig.h               # 生成的配置头文件
└── rtconfig.py              # 工具链配置
```

### 5.2 RT-Thread Nano（精简版）

无额外依赖，直接用 ARM GCC 编译。

```bash
# 1. 获取 RT-Thread Nano 源码
# 从 https://github.com/RT-Thread/rt-thread 下载
# 或在 CubeMX 中直接添加 RT-Thread Nano 软件包

# 2. 最小 Nano 源码（只需以下文件）
rt-thread/src/
├── clock.c
├── components.c
├── ipc.c
├── irq.c
├── kservice.c
├── mem.c
├── object.c
├── scheduler.c
├── thread.c
└── timer.c

rt-thread/include/            # 全部头文件

# 3. 编译（与 HAL 工程合并编译）
# 将 Nano 源文件加入 Makefile 的 SRCS 即可
```

---

## 6. 安装验证

安装完成后执行以下验证：

```bash
# 验证工具链
arm-none-eabi-gcc --version
arm-none-eabi-objcopy --version
arm-none-eabi-size --version
make --version
cmake --version

# 验证烧录工具（如已安装）
openocd --version
st-info --version

# 验证 SCons（如需 RT-Thread Standard）
scons --version

# 验证 CubeMX CLI（如已安装）
stm32cubeclt-cli --version
```

预期输出全部为版本号，无报错。

---

## 7. 能力矩阵总结

| 能力 | SPL | HAL | RT-Thread Nano | RT-Thread Standard |
|------|-----|-----|----------------|-------------------|
| 编译器 | arm-gcc | arm-gcc | arm-gcc | arm-gcc |
| 构建系统 | Makefile | Makefile/CMake | Makefile | SCons |
| 链接脚本 | 手动编写 | CubeMX 生成 | 手动/CubeMX | BSP 提供 |
| 启动文件 | 库自带 .s | 库自带 .s | 库自带 | BSP 提供 |
| 额外依赖 | 无 | CubeMX（可选） | 无 | scons |
| 工程生成 | 手动 | CubeMX CLI | 手动 | `scons --menuconfig` |
| IDE 兼容 | Makefile | Makefile + CubeMX | Makefile | `scons --target=mdk5` |

---

## 附录 A：WSL2 USB 设备直通

烧录需要 ST-Link 通过 USB 直通到 WSL2。问题在于 ST-Link 每次插拔的 USB 端口（busid）会变，因此需要用 **VID:PID** 方式绑定，不受端口影响。

### A.1 安装 usbipd-win

```powershell
winget install usbipd
```

### A.2 首次配置：按 VID:PID 绑定（一劳永逸）

```powershell
# 1. 查看设备，记下 ST-Link 的 VID:PID
usbipd list
# 示例输出：
# BUSID  VID:PID      DEVICE
# 3-4    0483:3748    ST-Link Debug, STMicroelectronics ST-LINK/V2
#               ↑↑↑↑:↑↑↑↑
#               这是 VID:PID，每次插拔都一样

# 2. 用 VID:PID 绑定（不受 busid 变化影响）
usbipd bind --hardware-id 0483:3748

# 3. 附加到 WSL
usbipd attach --wsl --hardware-id 0483:3748

# 4. 在 WSL 中验证
lsusb
# 应看到：STMicroelectronics ST-LINK/V2
```

> **ST-Link 常见 VID:PID**：
> | 型号 | VID:PID |
> |------|---------|
> | ST-Link/V2 | `0483:3748` |
> | ST-Link/V2-1 (Nucleo 板载) | `0483:374b` |
> | ST-Link/V3 | `0483:3754` |
> | ST-Link/V3 (DFU 模式) | `0483:df11` |

### A.3 设置自动附加（插上即用）

```powershell
# 设置自动附加规则：插上 ST-Link 自动直通到 WSL
usbipd auto-attach --wsl --hardware-id 0483:3748
```

执行后，每次插上 ST-Link 都会自动附加到 WSL，无需手动操作。

> 如果有多台调试器需要自动附加，重复执行即可（VID:PID 不同）。

### A.4 一键脚本：attach-stlink.ps1

保存为 `attach-stlink.ps1`，双击或命令行执行：

```powershell
# attach-stlink.ps1
# 自动查找并附加所有 ST-Link 设备到 WSL

$stlink_vids = @(
    "0483:3748",  # ST-Link/V2
    "0483:374b",  # ST-Link/V2-1
    "0483:3754",  # ST-Link/V3
    "0483:3753"   # ST-Link/V3E
)

foreach ($vid in $stlink_vids) {
    Write-Host "尝试绑定 $vid ..." -ForegroundColor Cyan
    usbipd bind --hardware-id $vid 2>$null
    usbipd attach --wsl --hardware-id $vid 2>$null
}

Write-Host "完成。在 WSL 中运行 lsusb 验证。" -ForegroundColor Green
```

### A.5 WSL 端配置 udev 规则（可选）

在 WSL 中创建 udev 规则，确保非 root 用户也能访问 ST-Link：

```bash
# WSL 中执行
sudo tee /etc/udev/rules.d/99-stlink.rules << 'EOF'
# ST-Link/V2
SUBSYSTEM=="usb", ATTR{idVendor}=="0483", ATTR{idProduct}=="3748", MODE="0666", GROUP="plugdev"
# ST-Link/V2-1
SUBSYSTEM=="usb", ATTR{idVendor}=="0483", ATTR{idProduct}=="374b", MODE="0666", GROUP="plugdev"
# ST-Link/V3
SUBSYSTEM=="usb", ATTR{idVendor}=="0483", ATTR{idProduct}=="3754", MODE="0666", GROUP="plugdev"
EOF

# 重新加载规则
sudo udevadm control --reload-rules
sudo udevadm trigger

# 将当前用户加入 plugdev 组
sudo usermod -aG plugdev $USER
```

### A.6 完整工作流

```
┌─────────────┐    attach     ┌────────────┐    openocd    ┌─────────────┐
│  ST-Link    │ ───────────→  │   WSL2     │ ───────────→  │   STM32     │
│  (Windows)  │  VID:PID 绑定 │  Ubuntu    │  flash 命令   │   芯片      │
└─────────────┘  自动附加      └────────────┘               └─────────────┘
```

**日常使用**：
1. 插上 ST-Link → 自动直通到 WSL（auto-attach）
2. WSL 中执行 `make flash` → OpenOCD 自动找到设备并烧录
3. 拔掉 ST-Link → 自动断开

**手动操作**（如果未设置 auto-attach）：
```powershell
# Windows PowerShell
usbipd attach --wsl --hardware-id 0483:3748   # 附加
usbipd detach --hardware-id 0483:3748          # 断开
```

## 附录 B：常用芯片对应参数速查

| 芯片 | Cortex | 浮点 | 启动文件 | HAL 包 | SPL 包 |
|------|--------|------|----------|--------|--------|
| STM32F103C8 | M3 | 无 | startup_stm32f10x_md.s | STM32CubeF1 | STM32F10x_StdPeriph |
| STM32F407IG | M4 | 硬件 FPU | startup_stm32f407xx.s | STM32CubeF4 | — |
| STM32F767ZI | M7 | 硬件 FPU | startup_stm32f767xx.s | STM32CubeF7 | — |
| STM32H743ZI | M7 | 硬件 FPU | startup_stm32h743xx.s | STM32CubeH7 | — |
| STM32G070RB | M0+ | 无 | startup_stm32g070xx.s | STM32CubeG0 | — |

## 附录 C：一键安装脚本

```bash
#!/bin/bash
# stm32-env-setup.sh — STM32 编译环境一键安装

set -e

echo "=== 安装基础工具链 ==="
sudo apt update
sudo apt install -y gcc-arm-none-eabi make cmake git python3 python3-pip

echo "=== 安装 SCons（RT-Thread Standard 所需）==="
pip3 install scons --break-system-packages

echo "=== 安装烧录工具 ==="
sudo apt install -y openocd stlink-tools

echo "=== 下载 HAL 固件包（F4）==="
cd ~
[ ! -d "STM32CubeF4" ] && git clone --depth 1 https://github.com/STMicroelectronics/STM32CubeF4.git

echo "=== 下载 RT-Thread ===="
[ ! -d "rt-thread" ] && git clone --depth 1 https://github.com/RT-Thread/rt-thread.git

echo "=== 验证安装 ==="
arm-none-eabi-gcc --version
scons --version
openocd --version

echo "=== 安装完成 ==="
echo "已安装：ARM GCC, Make, CMake, SCons, OpenOCD, ST-Link Tools"
echo "已下载：STM32CubeF4, RT-Thread"
```

使用：
```bash
chmod +x stm32-env-setup.sh
./stm32-env-setup.sh
```
