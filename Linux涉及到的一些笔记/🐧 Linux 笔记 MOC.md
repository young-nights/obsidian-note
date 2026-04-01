---
tags:
  - moc
created: 2026-04-01 17:02:00
type: MOC
status: active
folder: Linux涉及到的一些笔记
---

# 🐧 Linux 笔记 MOC

> Linux 系统、嵌入式开发、烧录工具等相关笔记汇总。

## 📋 概览

```dataviewjs
const statusMap = { active: "🟢 进行中", planning: "🟡 规划中", archived: "📦 已归档" };
const cur = dv.current();
dv.table(["属性", "值"], [
  ["状态", statusMap[cur.status] || "❓"],
  ["笔记数", cur.file.outlinks.length]
]);
```

## ⭐ 核心笔记

- [[Ubuntu-desktop配置]]

## 🗂️ 分类导航

### 嵌入式 & ARM

- [[Cortex-A7汇编语言]]
- [[IMX6U66启动方式]]

### 系统配置

- [[Ubuntu-desktop配置]]

### 工具 & 烧录

- [[.bin文件烧录进SD卡]]

### 子主题

- [[IMX6ULL开发笔记/IMX6U66启动方式|IMX6ULL 开发笔记 →]]

## 🔗 关联 MOC

- [[🖥️ Ubuntu-Server MOC]] — Ubuntu Server 配置

## 📌 待办 & 下一步

- [ ] 

## 🕐 最近修改

```dataviewjs
const notes = dv.pages('"Linux涉及到的一些笔记"')
  .where(p => p.file.ext === "md" && p.file.name !== dv.current().file.name && !p.file.path.includes("Templates") && !p.file.tags.includes("moc"))
  .sort(p => p.file.mtime, "desc");

dv.table(["笔记", "修改时间"], notes.map(p => [
  p.file.link,
  p.file.mtime.toFormat("DD HH:mm")
]));
```

## 📊 全部笔记（含子目录）

```dataviewjs
const notes = dv.pages('"Linux涉及到的一些笔记"')
  .where(p => p.file.ext === "md" && p.file.name !== dv.current().file.name && !p.file.path.includes("Templates") && !p.file.tags.includes("moc"))
  .sort(p => p.file.mtime, "desc");

dv.table(["笔记", "标签", "最后修改"], notes.map(p => [
  p.file.link,
  p.file.tags.join(", ") || "—",
  p.file.mtime.toFormat("DD HH:mm")
]));
```
