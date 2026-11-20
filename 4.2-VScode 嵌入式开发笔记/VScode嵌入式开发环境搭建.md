---
tags:
  - guide
  - config
created: 2026-11-13 06:12:23
---

# <font size=4>Windows + VScode 嵌入式开发环境搭建</font>

<font size=2>

本文档面向 **Windows + VSCode** 嵌入式开发环境搭建，目标工程为 `cpr-assessment-training-machine`（CPR 心肺复苏评估训练系统，多板 RT-Thread / 裸机工程）。内容包括：项目构建结构、工具链现状、VSCode 插件扫描结果、缺失项补齐，以及 CMake 方式编译的实测流程与踩坑记录。

> [!info] 扫描信息基准
> 插件与工具链扫描日期：2026-11-13。插件清单以 `code --list-extensions` 输出为准，工具版本为本机实测。

</font>

## <font size=3>一、目标工程与构建结构</font>

<font size=2>

`cpr-assessment-training-machine` 仓库包含 5 个子工程，构建体系各不相同：

| 子工程 | MCU | 构建体系 | VSCode 编译可行性 |
|--------|-----|---------|------------------|
| cpr-display-main-board | STM32F103ZE | RT-Thread + SCons | ✅ CMake 路线（本文实测通过） |
| cpr-sensor-board | STM32F103RC | RT-Thread + SCons | ✅ 同上（结构同构） |
| cpr-remote-device | STM32F103RF + LVGL | RT-Thread + SCons | ✅ 同上（含 LVGL 包） |
| cpr-head-board | STM32F103C6 | 裸机 Makefile | ✅ Makefile Tools 直接构建 |
| cpr-raster-board | STM8S003 | IAR EWSTM8 | ⚠️ 需 IAR 工具链（iarsystems 插件） |

> [!info] "CMake 结构"从哪来
> RT-Thread 工程执行 `scons --target=cmake` 会调用 `rt-thread/tools/cmake.py`，按当前 SConscript 注册的源码生成 `CMakeLists.txt`（仓库 .gitignore 已忽略该生成产物）。VSCode 安装 CMake Tools 插件后加载该 CMakeLists.txt，即可获得补全、构建、调试一体化体验。

</font>

## <font size=3>二、工具链现状与安装</font>

<font size=2>

本机已安装 **STM32CubeCLT 1.18.0**（`C:\ST\STM32CubeCLT_1.18.0`），各工具目录已加入 PATH：

| 工具 | 版本 | 来源 | 状态 |
|------|------|------|------|
| cmake | 3.28.1 | STM32CubeCLT | ✅ 已装 |
| ninja | 1.11.1 | STM32CubeCLT | ✅ 已装 |
| arm-none-eabi-gcc | 13.3.1（GNU Tools for STM32） | STM32CubeCLT | ✅ 已装 |
| STM32CubeProgrammer | — | STM32CubeCLT | ✅ 已装（烧录） |
| STLink GDB Server | — | STM32CubeCLT | ✅ 已装（调试） |
| Python | 3.13.15 | Python 官方安装包 | ✅ 已装 |
| scons | — | pip | ❌ 未装，构建 RT-Thread 工程必需 |

</font>

### <font size=2>2.1 安装 SCons（必需）</font>

<font size=2>

```powershell
# 必须锁定 4.4.x：4.5+ 与 RT-Thread building.py 不兼容（deque + list TypeError，实测）
pip install scons==4.4.0

# 验证
scons --version
```

</font>

### <font size=2>2.2 WSL 侧（可选备用）</font>

<font size=2>

WSL 已有 cmake 4.2.3、arm-none-eabi-gcc 14.2.1、make，scons 未装。若选择在 WSL 编译，同样 `pip install scons==4.4.0`，并在生成 CMakeLists 前导出环境变量：

```bash
export RTT_EXEC_PATH=/usr/bin   # 指向 arm-none-eabi-gcc 所在目录
export RTT_CC=gcc
```

</font>

## <font size=3>三、VSCode 插件扫描结果</font>

<font size=2>

扫描日期：2026-11-13（`code --list-extensions`，共 60+ 个插件）。与嵌入式 / CMake 开发相关的插件如下。

</font>

### <font size=2>3.1 已安装：C/C++ 构建与调试核心</font>

<font size=2>

| 插件 ID | 名称 | 用途 |
|---------|------|------|
| ms-vscode.cpptools | C/C++ | 智能补全、调试基础 |
| ms-vscode.cpptools-extension-pack | C/C++ Extension Pack | C/C++ 插件合集 |
| ms-vscode.cpptools-themes | C/C++ Themes | 主题 |
| ms-vscode.cpp-devtools | C/C++ Dev Tools | 诊断工具 |
| ms-vscode.makefile-tools | Makefile Tools | Makefile 工程（cpr-head-board 可用） |
| marus25.cortex-debug | Cortex-Debug | arm-none-eabi GDB 调试核心 |
| mcu-debug.debug-tracker-vscode | Debug Tracker | 调试会话跟踪 |
| mcu-debug.memory-view | Memory View | 内存查看 |
| mcu-debug.peripheral-viewer | Peripheral Viewer | 外设寄存器（可配 SVD，CubeCLT 自带 SVD 文件） |
| mcu-debug.rtos-views | RTOS Views | RT-Thread / FreeRTOS 线程视图 |
| vadimcn.vscode-lldb | CodeLLDB | LLDB 调试 |

</font>

### <font size=2>3.2 已安装：其他工具链与辅助</font>

<font size=2>

| 插件 ID | 名称 | 用途 |
|---------|------|------|
| cl.eide / cl.keil-assistant | EIDE / Keil Assistant | Keil MDK 工程导入与构建 |
| iarsystems.iar-build / iar-debug / iar-login | IAR Build/Debug | cpr-raster-board（IAR EWSTM8） |
| platformio.platformio-ide | PlatformIO | 跨平台嵌入式框架 |
| espressif.esp-idf-extension | ESP-IDF | ESP32 系列（本项目不涉及） |
| dan-c-underwood.arm | ARM Assembly | 启动文件 / 汇编高亮 |
| zixuanwang.linkerscript | LinkerScript | 链接脚本高亮 |
| xiaoyongdong.srecord / keroc.hex-fmt | srec / hex | 烧录文件格式支持 |
| ms-vscode.vscode-serial-monitor | Serial Monitor | 串口日志 |
| cschlosser.doxdocgen | Doxygen Documentation Generator | 注释生成 |
| xaver.clang-format | Clang-Format | 代码格式化 |
| ms-python.python / debugpy / pylance | Python | scons / Kconfig 依赖 |
| franneck94.c-cpp-runner | C/C++ Runner | 一键运行辅助 |

其余插件为 Markdown、Docker、远程开发、主题类，与嵌入式编译无直接关系。

</font>

### <font size=2>3.3 缺失插件（CMake 编译必需）</font>

<font size=2>

| 插件 ID | 名称 | 必要性 | 用途 |
|---------|------|--------|------|
| ms-vscode.cmake-tools | CMake Tools | ✅ 必装 | CMake 工程配置 / 构建 / 调试核心 |
| twxs.cmake | CMake | ✅ 建议装 | CMakeLists.txt 语法高亮 |

```powershell
code --install-extension ms-vscode.cmake-tools
code --install-extension twxs.cmake
```

> [!tip] 安装后验证
> 重启 VSCode，打开含 `CMakeLists.txt` 的目录，左下角应出现 CMake 状态栏（Kit / Build 按钮）。

</font>

## <font size=3>四、CMake 编译流程（实测）</font>

<font size=2>

以 `cpr-display-main-board` 为例（其余 RT-Thread 板同构）。整体流程：生成 CMakeLists → 补丁 → CMake Tools 构建。

</font>

### <font size=2>4.1 生成 CMakeLists.txt</font>

<font size=2>

```powershell
cd C:\Users\18452\Documents\github-nights\cpr-assessment-training-machine\cpr-display-main-board
set RTT_EXEC_PATH=C:\ST\STM32CubeCLT_1.18.0\GNU-tools-for-STM32\bin
set RTT_CC=gcc
scons --target=cmake
```

> [!warning] 这一步是 dry-run，不会真正编译
> `--target=cmake` 内部执行 `SetOption('no_exec', 1)`，只生成工程文件。控制台出现的 `CC ...` / `LINK ...` 字样是模拟输出，不代表构建成功，也不会产生 .o / .elf 文件。

> [!warning] 未设置 RTT_EXEC_PATH 会报错
> 报 `Cannot found toolchain directory, please check RTT_CC and RTT_EXEC_PATH` 时，按上面命令设置环境变量，指向 arm-none-eabi-gcc 所在目录。

</font>

### <font size=2>4.2 补丁 CMakeLists.txt（必需）</font>

<font size=2>

生成的 CMakeLists.txt 只包含 SConscript 注册的源码（RT-Thread 内核 + cubemx 2 个文件）。本仓库 `drivers/`、`applications/`、`libraries/` 三个目录缺少 SConscript，导致生成物缺失 HAL / CMSIS 头文件路径、编译宏和约 90 个源文件。解决办法：在 CMakeLists.txt 末尾追加以下补丁段（对照 RT-Thread Studio 生成的 `Debug/makefile` 逐项补齐，2026-11-13 实测通过）：

```cmake
# ===== SUPPLEMENT: patch cmake.py generator gaps (mirror Eclipse Debug/makefile) =====
TARGET_COMPILE_DEFINITIONS(${CMAKE_PROJECT_NAME}.elf PRIVATE
    SOC_FAMILY_STM32 SOC_SERIES_STM32F1 USE_HAL_DRIVER STM32F103xE STM32F10X_HD)
TARGET_COMPILE_OPTIONS(${CMAKE_PROJECT_NAME}.elf PRIVATE
    -mcpu=cortex-m3 -mthumb -ffunction-sections -fdata-sections
    -include ${CMAKE_SOURCE_DIR}/rtconfig_preinc.h)
SET_TARGET_PROPERTIES(${CMAKE_PROJECT_NAME}.elf PROPERTIES LINK_FLAGS
    "-mcpu=cortex-m3 -mthumb --specs=nano.specs -Wl,--gc-sections")

TARGET_INCLUDE_DIRECTORIES(${CMAKE_PROJECT_NAME}.elf PRIVATE
    drivers drivers/include drivers/include/config
    applications applications/macBSP/Inc applications/macNRF/Inc
    applications/macSYS/Inc applications/macFlash/Inc
    libraries/CMSIS/Include libraries/CMSIS/Device/ST/STM32F1xx/Include
    libraries/CMSIS/RTOS/Template
    libraries/STM32F1xx_HAL_Driver/Inc libraries/STM32F1xx_HAL_Driver/Inc/Legacy)

FILE(GLOB PATCH_SOURCES
    libraries/STM32F1xx_HAL_Driver/Src/*.c
    libraries/STM32F1xx_HAL_Driver/Src/Legacy/*.c
    libraries/CMSIS/Device/ST/STM32F1xx/Source/Templates/*.c
    libraries/CMSIS/Device/ST/STM32F1xx/Source/Templates/gcc/startup_stm32f103xe.S
    drivers/*.c
    applications/*.c
    applications/macBSP/Src/*.c
    applications/macFlash/Src/*.c
    applications/macNRF/Src/*.c
    applications/macSYS/Src/*.c
    applications/macTASK/*.c)
TARGET_SOURCES(${CMAKE_PROJECT_NAME}.elf PRIVATE ${PATCH_SOURCES})
```

> [!tip] 其他 RT-Thread 板的差异
> sensor / remote 板结构与 display 板同构，补丁段可直接复用，仅需按各自 `Debug/makefile` 或 `.cproject` 核对宏（如 `STM32F103xE` 对应 display 板，其他板是 `STM32F103xB` 等）与 `applications/` 下的模块目录名。启动文件名按实际芯片调整（如 `startup_stm32f103xb.S`）。

</font>

### <font size=2>4.3 CMake Tools 配置与构建</font>

<font size=2>

1. VSCode 打开板级目录（如 `cpr-display-main-board`，让 CMake Tools 能找到 CMakeLists.txt）
2. `Ctrl+Shift+P` → **CMake: Configure**，Kit 选择 `GCC 13.3.1 arm-none-eabi`（STM32CubeCLT 自带）
3. `Ctrl+Shift+P` → **CMake: Build**
4. 产物输出在 `cmake-build-debug/`：`rtthread.elf`、`rtthread.bin`

实测结果（2026-11-13，WSL 环境验证同一份补丁）：

```text
text    data     bss     dec     hex filename
130728    728   10408  141864   22a28 rtthread.elf
```

</font>

## <font size=3>五、备选构建路线</font>

<font size=2>

| 路线 | 工具 | 状态 |
|------|------|------|
| Makefile Tools + `Debug/makefile` | ms-vscode.makefile-tools（已装） | ✅ Eclipse/RT-Thread Studio 生成的 makefile 配置完整，Windows 侧需 GNU Make |
| EIDE 导入 Keil 工程 | cl.eide（已装） | ✅ 可导入 `cubemx/MDK-ARM/*.uvprojx` 构建烧录 |
| scons 直接构建 | scons | ❌ 当前不可用：`drivers/`、`applications/`、`libraries/` 缺 SConscript，HAL 头与源均未注册（报 `stm32f1xx_hal.h: No such file or directory`）。根治需补齐 SConscript |
| RT-Thread Studio / Eclipse | .cproject | ✅ 现成工程，Debug/ 下已有构建产物 |
| IAR EWSTM8 | iarsystems 插件 | ⚠️ 仅 cpr-raster-board 适用 |

</font>

## <font size=3>六、踩坑记录</font>

<font size=2>

| 日期 | 问题 | 解决方案 |
|------|------|----------|
| 2026-11-13 | `scons` 4.11 报 `TypeError: can only concatenate deque (not "list") to deque` | RT-Thread 旧版 building.py 与 SCons 4.5+ 不兼容，锁定 `pip install scons==4.4.0` |
| 2026-11-13 | `scons --target=cmake` 控制台显示编译链接成功但无产物 | 该命令是 dry-run（`no_exec=1`），CC/LINK 为模拟输出，属正常现象 |
| 2026-11-13 | 生成的 CMakeLists.txt 编译报 `stm32f1xx_hal.h: No such file or directory` | cmake.py 只收集 SConscript 注册源，按 4.2 节补丁段补齐宏 / 头路径 / 源文件 |
| 2026-11-13 | scons 报 `Cannot found toolchain directory` | 设置 `RTT_EXEC_PATH` 指向 arm-none-eabi-gcc 所在 bin 目录 |
| 2026-11-13 | WSL 下 CMake 选 Ninja generator 失败 | WSL 未装 ninja，改用 `-G "Unix Makefiles"`；Windows 侧 CubeCLT 自带 ninja 无此问题 |
| 2026-11-13 | 编译大量 `warning: "HAVE_CCONFIG_H" redefined` | rtconfig_preinc.h 与命令行宏重复定义，无害警告，可忽略 |

</font>
