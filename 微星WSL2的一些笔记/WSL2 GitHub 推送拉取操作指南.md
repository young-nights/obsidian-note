# WSL2 中推送 GitHub 仓库操作指南

## 前置条件

1. WSL2 已安装 Git：
   ```bash
   sudo apt update && sudo apt install git -y
   ```

2. 配置 Git 用户信息：
   ```bash
   git config --global user.name "young-nights"
   git config --global user.email "2863692760@qq.com"
   ```

3. 生成 SSH 密钥并添加到 GitHub：
   ```bash
   ssh-keygen -t ed25519 -C "2863692760@qq.com"
   cat ~/.ssh/id_ed25519.pub
   ```
   将输出的公钥复制到 GitHub → Settings → SSH and GPG keys → New SSH key

4. 验证 SSH 连接：
   ```bash
   ssh -T git@github.com
   ```

## 当前仓库列表

| 仓库名称 | 本地路径 (WSL2) | 远程地址 (SSH) | 分支 | 说明 |
|----------|----------------|---------------|------|------|
| ota-upgrade-of-qi-charger-based-on-can | `/home/whites/embedded_item/ota-upgrade-of-qi-charger-based-on-can` | `git@github.com:young-nights/ota-upgrade-of-qi-charger-based-on-can.git` | main | Qi 无线充 CAN-UDS OTA 升级项目 |
| obsidian-note | `/mnt/i/Obsidian note` | `git@github.com:young-nights/obsidian-note.git` | main | Obsidian 笔记仓库 |
| smart-ledger | `/home/whites/.openclaw/workspace/projects/smart-ledger` | `git@github.com:young-nights/smart-ledger.git` | main | 智能记账应用 |

> **新增仓库时**：在上表追加一行即可。

---

## 从零推送新仓库

### 方式一：本地已有代码，远程无仓库

```bash
# 1. 进入项目目录
cd /path/to/your/project

# 2. 初始化 Git
git init

# 3. 添加远程仓库（替换为你的仓库地址）
git remote add origin git@github.com:young-nights/仓库名.git

# 4. 添加所有文件并提交
git add -A
git commit -m "初始提交"

# 5. 推送
git push -u origin main
```

> **注意**：GitHub 新建仓库时**不要勾选** README / .gitignore / license，否则远程会有初始提交，本地推送会冲突。

### 方式二：GitHub 已有仓库，本地拉取

```bash
# 1. 克隆远程仓库
git clone git@github.com:young-nights/仓库名.git

# 2. 将代码复制到克隆目录中

# 3. 提交并推送
cd 仓库名
git add -A
git commit -m "添加代码"
git push
```

---

## 日常推送流程

```bash
# 1. 拉取远程最新代码
git pull

# 2. 查看变更状态
git status

# 3. 添加所有变更文件
git add -A

# 4. 提交
git commit -m "提交说明"

# 5. 推送
git push
```

---

## WSL2 访问 Windows 文件系统的注意事项

- Windows 磁盘挂载在 `/mnt/` 下，例如 `I:\GitHub` 对应 `/mnt/i/GitHub`
- **在 `/mnt/` 路径下操作 Git 速度较慢**，建议将项目放在 WSL2 原生文件系统中（如 `~/` 或 `/home/whites/`）
- 如果必须在 `/mnt/` 下操作，可以配置 Git 关闭文件系统监控加速：
  ```bash
  git config --global core.fsmonitor false
  ```

---

## 常见问题

### Q: SSH 权限报错 `Permission denied (publickey)`

```bash
# 检查 SSH agent 是否运行
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 确认远程地址是 SSH 协议
git remote -v
# 如果显示 https://，改为 SSH：
git remote set-url origin git@github.com:young-nights/仓库名.git
```

### Q: 推送被拒绝 `rejected - non-fast-forward`

```bash
# 先拉取再推送
git pull --rebase origin main
git push origin main

# 强制推送（⚠️ 谨慎使用，会覆盖远程）
git push --force-with-lease origin main
```

### Q: 如何查看远程分支列表

```bash
git branch -r
```

### Q: 如何切换远程分支

```bash
# 切换到指定分支
git checkout -b 本地分支名 origin/远程分支名
```

---

## 变更记录

| 版本 | 日期 | 改动点 |
|------|------|--------|
| v1.0 | 2026-08-31 | 初始版本，包含 WSL2 推送 GitHub 完整操作指南 |
| v1.1 | 2026-09-01 | 新增「当前仓库列表」表格，填入 3 个仓库实际路径和远程地址；补充 `git pull --rebase` 方案；用户信息改为实际值 |
