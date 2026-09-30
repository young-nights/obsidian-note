# 固件发布 MD5 打包、解包与验证指南

> 来源：`docs/JYF_Qi_充电器固件发布与交付要求_v1.01_中文提炼.md` 中 MD5 相关要求（规则部分忠实提取），配套方法指令与测试为可直接执行的例程。
> 适用：JYF → Lime 固件发布交付流程。例程在 WSL2 / Ubuntu 下验证通过。

---

## 一、规则速览（来自交付要求 v1.01）

1. 文件命名内嵌完整 32 字符 MD5：`QC_JYF_MCU1_FW_1.1.x_<MD5>.img` / `.bin`（MCU2 同理）
2. `<MD5>` 为**最终发布文件内容**的完整 32 字符 MD5，`.img` 与 `.bin` **各自独立计算**
3. 同一版本同时交付 `.img` 与 `.bin` 时，两者使用**相同的固件版本号**
4. 已发布文件**不得**在版本号与文件名不变的情况下被修改或替换；任何变更必须升版本号
5. 发布包结构（`.zip`）：

```
QC_JYF_MCU1_FW_1.1.x_MCU2_FW_1.1.y_Release/
├── Firmware/
│   ├── MCU1/   *.img + *.bin（文件名含 32 字符 MD5）
│   └── MCU2/   *.img + *.bin
├── Release_Note/    *_Release_Note.pdf（须列出每个文件完整 MD5）
├── Test_Report/     *_Self_Test_Report.pdf（须记录测试文件完整 MD5）
└── Checksum/        MD5.txt（列出每个发布文件及其完整 MD5）
```

6. 三处记录必须与包内实测一致：Release Note、自测报告、交付邮件，每个 `.img`/`.bin` 的完整 MD5
7. 自测必须基于**交付给 Lime 的同一份固件文件**（OTA 测试用 `.img`）
8. 发布前置条件包含：**每个文件 MD5 校验**；GitHub Release 上传文件须与交付文件完全一致，不得静默替换

---

## 二、打包：计算 MD5 并写入文件名

在发布包根目录执行（例：`QC_JYF_MCU1_FW_1.1.1_MCU2_FW_1.1.1_Release/`）：

```bash
# 计算单文件 MD5
md5sum QC_JYF_MCU1_FW_1.1.1_app.bin

# 批量计算
md5sum Firmware/MCU1/* Firmware/MCU2/*
```

把 MD5 追加进文件名（重命名不改变内容 MD5，顺序必须是"先算后改名"）：

```bash
f=Firmware/MCU1/QC_JYF_MCU1_FW_1.1.1_app.bin
md5=$(md5sum "$f" | cut -d' ' -f1)
mv "$f" "$(dirname "$f")/QC_JYF_MCU1_FW_1.1.1_${md5}.bin"
```

`.img` 同样独立执行一遍（MD5 各自计算，两文件 MD5 不同属正常）。

---

## 三、生成 Checksum/MD5.txt

```bash
# 发布包根目录执行；标准 md5sum 格式，可直接 md5sum -c 校验
mkdir -p Checksum
find Firmware -type f \( -name '*.img' -o -name '*.bin' \) \
  -exec md5sum {} + > Checksum/MD5.txt
```

生成示例（格式）：

```
d921c88de7ee0f954f266b0da7a77ad0  Firmware/MCU1/QC_JYF_MCU1_FW_1.1.1_d921c88….bin
```

---

## 四、打包 zip

```bash
# 需 zip：sudo apt install zip unzip
zip -r ../QC_JYF_MCU1_FW_1.1.1_MCU2_FW_1.1.1_Release.zip .
```

无 zip 时用 Python 标准库（免安装，本机已验证）：

```bash
python3 -m zipfile -c ../QC_JYF_MCU1_FW_1.1.1_MCU2_FW_1.1.1_Release.zip .
```

> 交付判据是**包内文件的 MD5**（MD5.txt），不是 zip 压缩包本体的 MD5——压缩实现不同会导致 zip 字节不同。

---

## 五、解包与验证

```bash
# 方式一：unzip（需安装）
unzip QC_JYF_MCU1_FW_1.1.1_MCU2_FW_1.1.1_Release.zip -d deliver_check

# 方式二：Python 标准库（免安装，本机已验证）
python3 -m zipfile -e QC_JYF_MCU1_FW_1.1.1_MCU2_FW_1.1.1_Release.zip deliver_check
```

整包校验（在解包后的发布包根目录执行，全部 `OK` 即通过，任一 `FAILED` 即失败）：

```bash
cd deliver_check
md5sum -c Checksum/MD5.txt
```

单文件复核 / 与交付邮件比对：

```bash
md5sum Firmware/MCU1/*.img Firmware/MCU1/*.bin
```

---

## 六、文件名 MD5 后缀一致性脚本

校验"文件名里的 32 位 MD5 == 文件实际内容 MD5"，在发布包根目录执行：

```bash
#!/usr/bin/env bash
fail=0
while IFS= read -r f; do
  stem="${f%.*}"                 # 去扩展名
  name_md5="${stem##*_}"          # 文件名最后一段 = 32 位 MD5
  real_md5="$(md5sum "$f" | cut -d' ' -f1)"
  if [ "$name_md5" = "$real_md5" ]; then
    echo "OK   $f"
  else
    echo "FAIL $f (文件名=$name_md5 实际=$real_md5)"
    fail=1
  fi
done < <(find Firmware -type f \( -name '*.img' -o -name '*.bin' \))
exit $fail
```

---

## 七、MD5 相关测试清单

依据交付要求第 5、7、11、13 节整理，发布前逐项执行：

| ID | 测试项 | 步骤 | 判定 |
|----|--------|------|------|
| M1 | 文件名后缀一致 | 运行第六节脚本 | 全部 OK |
| M2 | 包内清单校验 | 解包后 `md5sum -c Checksum/MD5.txt` | 全部 OK，无 FAILED |
| M3 | 三处记录一致 | 解包实测 MD5 与 Release Note、自测报告、交付邮件逐一比对 | 三处完全一致 |
| M4 | 独立计算确认 | 分别计算 `.img` 与 `.bin` | 各自 32 字符；同版本号一致，MD5 不必相同 |
| M5 | 测试样本身份 | 自测报告（OTA 用 `.img`）记录的 MD5 == 交付包内该文件实测 MD5 | 一致 |
| M6 | 不可变性 | GitHub Release 重新下载，复算 MD5 | 与首次交付一致，有差异即拒收并升版本重发 |
| M7 | 校验项入检查表 | 发布前置 checklist 勾选"每个文件 MD5 校验" | 已完成并留档 |

任一测试 FAIL：修改必然触发版本号递增，回到第二节重新打包；强制项失败未经 Lime 明确批准不得发布。

---

## 八、常见坑

- `md5sum` 输出为**小写**十六进制，文件名与记录统一用小写
- MD5 基于**文件内容**：移动、重命名不影响；改动任何一个字节 → MD5 变 → 必须升版本号（"同名同版本不得替换"）
- `.img` 与 `.bin` 内容不同（`.img` 仅应用，`.bin` 含 bootloader），MD5 必然不同，属设计预期
- `md5sum -c` 的路径基准 = 生成 `MD5.txt` 时的工作目录（发布包根目录），换目录执行会报 No such file
- zip 本体 MD5 不稳定（压缩参数/工具版本差异），不要拿它当交付判据
- 记录 MD5 时抄错位数：比对前确认恰好 32 个字符

---

## 变更记录

| 版本 | 日期 | 改动内容 |
|------|------|----------|
| V1.0 | 2026-09-30 | 初版：从 JYF 发布交付要求 v1.01 提取 MD5 打包/解包/验证规则，配套已验证指令（md5sum / python3 zipfile / 后缀比对脚本）与 7 项测试清单 |
