# WSL2 串口数据抓取配置指南

> 适用于 Windows 11 + WSL2 (Ubuntu-24.04)。记录 USB 串口 / CAN 接到 WSL2、给本机工具或智能体直接读总线的流程。
> 创建日期：2026-09-16
> 本机发行版：Ubuntu-24.04；内核 `6.6.87.2-microsoft-standard-WSL2`；`usbipd-win` 5.3.0

---

## 一、背景

WSL2 是独立 Linux 内核的轻量虚拟机。**USB 和 COM 口不会自动出现在 WSL 里。**

两件容易踩的事实：

1. WSL2 里的 `/dev/ttyS0`～`/dev/ttyS7` 是虚拟端口，对应不了 Windows 设备管理器里的 COM3 / COM5 / CH340。要读真实 USB 转串口，必须走 `usbipd`。
2. 一只 USB 设备同一时刻只能给一边：`usbipd attach` 之后 Windows 上这个 COM / 调试器会消失；要还给 Windows 就 `detach`。

| 方案 | 适用场景 | 复杂度 |
|------|----------|--------|
| usbipd-win 把 USB 交给 WSL | 智能体或 minicom 直接打开 `/dev/ttyUSB*` / `/dev/ttyACM*` | 中 |
| Windows 侧抓取 + 共享文件 | 只录日志，不交互 | 低 |
| CAN：COM9 串口 CAN + python-can slcan | **当前在用**。设备管理器是 COM9，attach 进 WSL 当串口收 CAN | 中 |
| CAN：CANable gs_usb（pyusb） | 另有 candleLight 盒子时 | 中 |
| CAN：ZCANPRO TCP 桥 | 周立功盒子留在 Windows，WSL 连转发 | 中 |

本机已经装好、智能体可直接调用的软件：

| 位置 | 内容 |
|------|------|
| Windows | `usbipd-win` 5.3.0（`usbipd.exe` 在 PATH 里） |
| WSL | `usbutils`、`can-utils`、`socat`、`python3-serial` 3.5、`python3-can` 4.3.1、`python3-usb` |
| 账号 | `whites` 已加入 `dialout`、`plugdev`（**新开一个终端**后免 sudo 开串口） |

内核驱动：CH340 / CP210 / FTDI / CDC ACM 都有。`CONFIG_CAN=m` 有，**`CONFIG_CAN_GS_USB`、`CONFIG_CAN_SLCAN` 都没开**——WSL 里不会出现 `can0` / `slcan0`。当前 CAN 工具是**串口 CAN（COM9）**，不靠内核 slcan，见第七节。

---

## 二、方案一：usbipd-win（推荐，智能体走这条）

### 2.1 原理

Windows 用 `usbipd` 把 USB 设备以 USB/IP 附加到 WSL2 内核。Linux 识别为：

- `/dev/ttyUSB*`：CH340 / CP2102 / FT232
- `/dev/ttyACM*`：USB CDC（STM32 虚拟串口、部分调试器 CDC）

### 2.2 Windows 侧安装

本机已安装。若重装，管理员 PowerShell：

```powershell
winget install usbipd
```

重开终端后：

```powershell
usbipd --version
```

### 2.3 查看设备列表

```powershell
usbipd list
```

输出示例：

```
BUSID  VID:PID    DEVICE                                                        STATE
1-3    1a86:7523  USB-SERIAL CH340 (COM5)                                       Not shared
7-2    3562:0101  USB 串行设备 (COM9)                                           Not shared
7-4    2e3c:f000  USB 串行设备 (COM7), AT-Link-Plus(WinUSB) CMSIS-DAP            Not shared
```

记下 **BUSID**。`STATE`：`Not shared` 尚未 bind；`Shared` 已 bind、还在 Windows；`Attached` 已进 WSL。

### 2.4 绑定并附加

管理员 PowerShell：

```powershell
# 绑定（仅首次，重启后仍在）
usbipd bind --busid 1-3

# 本机若出现 hrdevmon 警告，改强制绑定（见 8.3）
usbipd bind --busid 1-3 --force

# 附加到 WSL2（不需要管理员；WSL 重启后要再做一次）
usbipd attach --wsl --busid 1-3

# 希望拔插/WSL 重启后自动再挂上
usbipd attach --wsl --auto-attach --busid 1-3
```

指定发行版（本机是 Ubuntu-24.04）：

```powershell
usbipd attach --wsl Ubuntu-24.04 --busid 1-3
```

还给 Windows：

```powershell
usbipd detach --busid 1-3
```

彻底取消共享：

```powershell
usbipd unbind --busid 1-3
```

### 2.5 本机设备注意（2026-09-25 实况）

`usbipd list` 当时在线的相关口：

| BUSID | VID:PID | Windows 名称 | 给 WSL 时 |
|-------|---------|--------------|-----------|
| 7-2 | `3562:0101` | USB 串行设备 **(COM9)** | **当前串口 CAN**。attach 后在 WSL 是 `/dev/ttyACM*` 或 `/dev/ttyUSB*`，见第七节 |
| 7-4 | `2e3c:f000` | COM7 + **AT-Link-Plus CMSIS-DAP** | **不要 attach**：一挂到 WSL，Keil / SWD 立刻没了 |

设备管理器里还有一批 CH340（COM3/4/5/6/8/12/13）。状态是 Unknown 时，多半是幽灵端口（设备已拔），`usbipd list` 的 **Connected** 里不会出现。CH340 重新插上后再 `usbipd list` 才能 bind。

### 2.6 WSL2 内确认

```bash
lsusb
ls -l /dev/ttyUSB* /dev/ttyACM*
dmesg | tail -30
```

正常类似：

```
ch341-uart converter now attached to ttyUSB0
```

`Permission denied`：当前这个终端还没吃到 `dialout`，**新开一个 WSL 终端**，或暂时 `sudo`。已经执行过：

```bash
sudo usermod -aG dialout,plugdev $USER
```

### 2.7 安装串口工具

智能体侧 `pyserial` 已装。人要交互终端时再装：

```bash
sudo apt update
sudo apt install minicom screen picocom moreutils -y
```

### 2.8 实时抓取

#### 波特率先对齐硬件

| 对象 | MCU 脚 | 接法 | 波特率 |
|------|--------|------|--------|
| Qi 无线充芯片 UART | PA2 MCU_TX / PA3 MCU_RX | **只听**：CH340 RX ← PA2，共地。CH340 TX 不要接到 PA3 | **9600 8N1** |
| MCU Debug（预留） | PB6 TX / PB7 RX | CH340 RX ← PB6，TX → PB7，共地 | 固件里目前基本没开 |

Qi 口是 MCU↔无线充芯片的内部总线，并联监听即可。

#### pyserial（智能体默认用这个）

```bash
python3 -c "import serial; s=serial.Serial('/dev/ttyUSB0', 9600, timeout=1); print(s.read(64))"
```

持续打印：

```bash
python3 -m serial.tools.miniterm /dev/ttyUSB0 9600 --raw
```

#### minicom

```bash
minicom -D /dev/ttyUSB0 -b 9600
# 退出：Ctrl+A 然后 X
```

#### picocom

```bash
picocom -b 9600 /dev/ttyUSB0
# 退出：Ctrl+A 然后 Ctrl+X
```

#### 纯录制

```bash
stty -F /dev/ttyUSB0 9600 raw -echo
cat /dev/ttyUSB0 | tee serial_capture_$(date +%Y%m%d_%H%M%S).log
```

带时间戳（需 `moreutils` 的 `ts`）：

```bash
stty -F /dev/ttyUSB0 9600 raw -echo
cat /dev/ttyUSB0 | ts '%Y-%m-%d %H:%M:%.S' | tee serial.log
```

---

## 三、方案二：Windows 侧抓取 + WSL2 读取

不把 USB 交给 WSL 时，Windows 抓、WSL 读共享盘。智能体只能读日志文件，看不到实时 `/dev/ttyUSB*`。

### 3.1 Windows 侧抓取

PuTTY 的 plink：

```powershell
plink -serial COM5 -sercfg 9600,8,n,1,N > C:\serial_capture.log
```

PowerShell：

```powershell
$port = New-Object System.IO.Ports.SerialPort COM5,9600,None,8,One
$port.Open()
while ($true) {
    $line = $port.ReadLine()
    $stamp = Get-Date -Format "HH:mm:ss.fff"
    Add-Content -Path "C:\serial_capture.log" -Value "[$stamp] $line"
}
```

### 3.2 WSL2 实时读取

```bash
tail -f /mnt/c/serial_capture.log
```

---

## 四、智能体怎么读串口

环境齐了、CH340 已经 `attach` 之后，直接说「监听串口」即可。智能体在 WSL 里跑的就是上面的 `pyserial` / `miniterm`。

开工前确认这三句都有输出：

```bash
usbipd.exe list          # 目标 BUSID 为 Attached
lsusb                    # 能看到 CH340 / USB Serial
ls /dev/ttyUSB* /dev/ttyACM*
```

把 BUSID 和 `/dev/ttyUSB*` 告诉智能体，避免猜错口。

---

## 五、WSL1 与 WSL2 的差异

| 特性 | WSL1 | WSL2 |
|------|------|------|
| 串口 | 可映射 `/dev/ttyS3` ↔ COM4 | 必须 usbipd |
| 内核 | 翻译层 | 独立 Linux 内核 |
| USB | 驱动映射 | USB/IP |

串口极频繁且没有 USB-CAN 需求时，可临时切 WSL1：

```powershell
wsl --set-version Ubuntu-24.04 1
wsl --set-version Ubuntu-24.04 2
```

本机日常保持 WSL2。切版本会改发行版后端，先备份再做。

---

## 六、操作速查（串口）

```powershell
# === Windows PowerShell ===
usbipd list
usbipd bind --busid 1-3
usbipd bind --force --busid 1-3          # hrdevmon 时
usbipd attach --wsl --busid 1-3
usbipd attach --wsl --auto-attach --busid 1-3
usbipd detach --busid 1-3
```

```bash
# === WSL2 ===
lsusb
ls /dev/ttyUSB* /dev/ttyACM*
python3 -m serial.tools.miniterm /dev/ttyUSB0 9600 --raw
stty -F /dev/ttyUSB0 9600 raw -echo
cat /dev/ttyUSB0 | tee serial.log
```

一键附加批处理示例 `attach_serial.bat`（BUSID 改成自己的）：

```bat
@echo off
usbipd attach --wsl --busid 1-3
echo Serial device attached to WSL2.
pause
```

---

## 七、CAN：给智能体读总线

**当前用的 CAN 工具是串口 CAN**：插上后设备管理器显示 **COM9**（`usbipd list` 里是 BUSID `7-2`，VID:PID `3562:0101`，名称「USB 串行设备 (COM9)」）。不是周立功 USBCAN 那种 WinUSB 盒子，也不是 gs_usb 网卡。

它在 Windows 上就是一个 COM 口；`usbipd attach` 进 WSL 后变成 `/dev/ttyACM*` 或 `/dev/ttyUSB*`。智能体用 **python-can 的 `slcan` 用户态**直接跟这个串口说话，**不需要**内核 `CONFIG_CAN_SLCAN`，也不会出现 `can0`。

COM9 **同一时刻只能给一边**：attach 之后 Windows 上 COM9 会消失（ZCANPRO / 串口助手都打不开这只盒子）；要还给 Windows 就 `detach`。

Qi 充电器 CAN：**250 kbps、Classical CAN、29-bit 扩展帧**。关注 ID：

| ID | 用途 |
|----|------|
| `0x18DA0D03` | UDS 请求（扩展帧，日志里带 `x`） |
| `0x18DA030D` | UDS 应答 |
| `0x18FF260D` | 生命周期 / Safe mode 心跳 |
| `0x18FF480D` | Boot 诊断标记 M1～M4 |

M1～M4 只在 Boot 里发，窗口大约几十毫秒。脚本先开、再给 MCU 上电。OTA 不更新 Boot。

### 7.1 方案 A（当前，推荐）：COM9 串口 CAN → WSL slcan

1. Windows 管理员 PowerShell 绑定（仅首次）：

```powershell
usbipd list
usbipd bind --busid 7-2
# 若 hrdevmon 警告导致 bind 失败：
usbipd bind --force --busid 7-2
```

2. 附加到 WSL（WSL 重启后要再做；BUSID 拔插后可能变，以 `usbipd list` 为准）：

```powershell
usbipd attach --wsl --busid 7-2
# 或
usbipd attach --wsl --auto-attach --busid 7-2
```

3. WSL 里确认口：

```bash
lsusb                    # 应看到 3562:0101
ls -l /dev/ttyACM* /dev/ttyUSB*
dmesg | tail -20
```

CDC 类一般是 `/dev/ttyACM0`，CH341 类 UART 是 `/dev/ttyUSB0`。下面以 `/dev/ttyACM0` 为例，实际以 `ls` 为准。

4. 智能体收 CAN（python-can 已装）。`slcan` 走串口 ASCII，不创建 `can0`：

```python
import can

# bitrate 是 CAN 总线速率，不是 COM 波特率
bus = can.Bus(interface="slcan", channel="/dev/ttyACM0", bitrate=250000)
for msg in bus:
    ext = "x" if msg.is_extended_id else " "
    print("%08X%s  %s" % (msg.arbitration_id, ext, msg.data.hex()))
```

串口侧常见 115200；若打不开通道或全是乱码，把 python-can 的 tty 波特率改成 `115200` / `1000000` / `2000000` 再试（部分适配器固件固定 1M）。

```python
bus = can.Bus(
    interface="slcan",
    channel="/dev/ttyACM0",
    ttyBaudrate=115200,
    bitrate=250000,
)
```

5. 还给 Windows（ZCANPRO 或设备管理器要重新看到 COM9）：

```powershell
usbipd detach --busid 7-2
```

### 7.2 方案 B：CANable / candleLight + pyusb

另有 **gs_usb** 盒子时用这个。COM9 那只串口 CAN **不要**配 `interface="gs_usb"`。

```python
import can
bus = can.Bus(interface="gs_usb", channel=0, bitrate=250000)
for msg in bus:
    print("%08X  %s" % (msg.arbitration_id, msg.data.hex()))
```

### 7.3 方案 C：周立功盒子 + ZCANPRO 留在 Windows

周立功 USBCAN **不要** attach 进 WSL：没有 `zcanpro` 模块，内核也认不成网卡。

```
[USBCAN] → ZCANPRO 扩展脚本 监听 TCP → WSL python 连 Windows 主机 IP
```

WSL 里看 Windows 主机地址：

```bash
ip route | awk '/default/ {print $3}'
```

智能体读的是转发文本/JSON。桥接脚本需要时再写进仓库 `python_tools/`。

### 7.4 不要做的

- 把 AT-Link-Plus（BUSID `7-4`）attach 进 WSL 来「顺带」看串口
- 指望 `/dev/ttyS*` 对应 COM9
- 指望默认 WSL 内核出现 `can0`（没编 `gs_usb` / `slcan`）
- COM9 还挂在 Windows 时，在 WSL 里找这只 CAN
- 把 COM9 当 Qi 芯片 9600 UART 来听（那是 CH340，见 2.8）

---

## 八、常见问题排查

### 8.1 `/dev/ttyUSB0` 不存在

```bash
lsusb
dmesg | grep -iE 'usb|ttyUSB|ch341|cp210|ftdi|cdc_acm'
usbipd.exe list
```

`usbipd list` 里目标设备不是 `Attached`：回到 Windows 做 attach。CH340 在设备管理器里是 Unknown、list 的 Connected 没有它：先重新插拔。

### 8.2 `usbipd attach` 报错

| 错误 | 原因 | 处理 |
|------|------|------|
| `error: WSL2 is not running` | WSL 没起来 | 先开一个 `wsl` 再附加 |
| `error: device not found` | BUSID 过期（拔插后会变） | 重新 `usbipd list` |
| `error: access denied` | bind 需要管理员 | 管理员 PowerShell 做 bind |
| `error: device is already attached` | 重复附加 | `usbipd detach --busid X-X` |
| Windows 串口助手打不开该 COM | 已经交给 WSL | `usbipd detach` |

`attach --wsl` 本身可以不提权；**`bind` 要管理员**。

### 8.3 `Unknown USB filter 'hrdevmon'` 警告

```
usbipd: warning: Unknown USB filter 'hrdevmon' may be incompatible with this software; 'bind --force' may be required.
```

`hrdevmon` 是 Windows 上的第三方 USB 过滤驱动。usbipd 扫描到它会提醒。**这是提示，不是失败。**

常见来源：企业 DLP、厂商设备套件、安全软件、烧录器/调试器自带驱动。本机已经出现过这条。

```powershell
usbipd bind --busid 1-3
# bind 失败，或 attach 后 WSL 看不到设备：
usbipd bind --force --busid 1-3
usbipd attach --wsl --busid 1-3
```

`--force` 让 usbipd 优先接管**这一只**设备。Windows 上原监控软件可能丢对它的控制。恢复：

```powershell
usbipd unbind --busid 1-3
```

### 8.4 读取乱码

```bash
stty -F /dev/ttyUSB0
```

先对齐硬件：Qi UART 是 **9600 8N1**，不是 115200。再试 38400 / 57600 / 115200 / 921600。

### 8.5 WSL2 重启后设备丢失

`attach` 默认是会话级。WSL 重启、`wsl --shutdown`、拔线都会断。每次启动后重新 attach，或用 `--auto-attach`。

### 8.6 `Permission denied`

新开终端。确认：

```bash
id
# 应含 dialout
ls -l /dev/ttyUSB0
```

### 8.7 智能体能开串口、CAN 仍是空的

CH340 是 Qi UART（9600），COM9 是串口 CAN，两套硬件。

- `usbipd list` 里 `7-2` 不是 `Attached`：先 attach COM9
- WSL 有 `/dev/ttyACM0` 但 python-can 无帧：CAN 速率必须是 **250000**；确认 CANH/CANL 和共地
- `slcan` 报错打不开：换 `ttyBaudrate`（115200 / 1000000）
- Windows 还能看到 COM9：设备还在 Windows 侧，WSL 抢不到

---

## 变更记录

| 版本 | 日期 | 改动内容 |
|------|------|----------|
| V1.0 | 2026-09-16 | 初版：usbipd-win、Windows 侧抓取、WSL1/WSL2 差异、常见问题 |
| V1.1 | 2026-09-16 | 5.3（现 8.3）：hrdevmon 警告、`--force` 与恢复 |
| V1.2 | 2026-09-25 | 本机实况（usbipd 5.3.0、已装 pyserial/python-can、dialout）；`/dev/ttyS*` 与 COM 的关系；设备互斥；AT-Link 不要 attach；Qi UART 9600 只听接法；智能体读串口步骤；CAN 方案 A（CANable/pyusb）与方案 B（ZCANPRO TCP 桥）；内核无 gs_usb/slcan；auto-attach |
| V1.3 | 2026-09-25 | 当前 CAN 工具改为 COM9 串口 CAN（`3562:0101` / BUSID `7-2`）；第七节主路径改为 usbipd + python-can `slcan` 用户态；内核无 slcan 模块不影响；CH340 与 COM9 分工写进 8.7 |
|
