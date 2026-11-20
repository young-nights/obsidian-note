---
tags:
  - moc
created: 2026-04-01 17:02:00
type: MOC
status: active
folder: Ubuntu-Server配置笔记
---

# 🖥️ Ubuntu-Server 配置 MOC

> Ubuntu Server 环境搭建、开发环境配置、网络代理等笔记。

## 📋 概览

```dataviewjs
const statusMap = { active: "🟢 进行中", planning: "🟡 规划中", archived: "📦 已归档" };
const cur = dv.current();
const noteCount = dv.pages('"Ubuntu-Server配置笔记"')
  .where(p => p.file.ext === "md" && p.file.name !== cur.file.name && !p.file.path.includes("Templates"))
  .length;
dv.table(["属性", "值"], [
  ["状态", statusMap[cur.status] || "❓"],
  ["笔记数", noteCount]
]);
```

## ⭐ 核心笔记

- [[Ubuntu-Server配置]]

## 🗂️ 分类导航

### 基础配置

- [[Ubuntu-Server配置]]

### 开发环境

- [[Ubuntu-Server-ESP32开发环境搭建]]
- [[Ubuntu-Server-Git环境搭建]]
- [[Ubuntu-Server-OpenMV开发环境搭建]]

### 网络与代理

- [[Ubuntu-Server-网络代理配置]]

## 🔗 关联 MOC

- [[🐧 Linux 笔记 MOC]] — Linux 通用笔记

## 📌 待办 & 下一步

- [ ] 

## 🐛 问题日志

| 日期 | 问题 | 解决方案 | 关联笔记 |
|------|------|----------|----------|
|  |  |  |  |

## 🕐 最近修改

```dataviewjs
const notes = dv.pages('"Ubuntu-Server配置笔记"')
  .where(p => p.file.ext === "md" && p.file.name !== dv.current().file.name && !p.file.path.includes("Templates") && !p.file.tags.includes("moc"))
  .sort(p => p.file.mtime, "desc");

dv.table(["笔记", "修改时间"], notes.map(p => [
  p.file.link,
  p.file.mtime.toFormat("DD HH:mm")
]));
```

## 📊 全部笔记

```dataviewjs
const notes = dv.pages('"Ubuntu-Server配置笔记"')
  .where(p => p.file.ext === "md" && p.file.name !== dv.current().file.name && !p.file.path.includes("Templates") && !p.file.tags.includes("moc"))
  .sort(p => p.file.mtime, "desc");

dv.table(["笔记", "标签", "最后修改"], notes.map(p => [
  p.file.link,
  p.file.tags.join(", ") || "—",
  p.file.mtime.toFormat("DD HH:mm")
]));
```
