---
tags:
  - moc
created: 2026-04-01 17:02:00
type: MOC
status: archived
folder: IndexTTS本地部署[文本转语音]
---

# 🎙️ IndexTTS 本地部署 MOC

> IndexTTS（旧版）文本转语音模型的本地部署记录。

## 📋 概览

```dataviewjs
const statusMap = { active: "🟢 进行中", planning: "🟡 规划中", archived: "📦 已归档" };
const cur = dv.current();
const noteCount = dv.pages('"IndexTTS本地部署[文本转语音]"')
  .where(p => p.file.ext === "md" && p.file.name !== cur.file.name && !p.file.path.includes("Templates"))
  .length;
dv.table(["属性", "值"], [
  ["状态", statusMap[cur.status] || "❓"],
  ["笔记数", noteCount]
]);
```

## ⭐ 核心笔记

- [[IndexTTS本地部署文档]]

## 🗂️ 分类导航

### 部署流程

- [[IndexTTS本地部署文档]]

### 依赖安装

- [[Windows安装FFmpeg]]
- [[Windows安装Miniconda]]
- [[安装Pytroch]]

### 问题记录

- [[问题详述]]

## 🔗 关联 MOC

- [[🎙️ IndexTTS-2 MOC]] — 新版，推荐使用

## 📊 全部笔记

```dataviewjs
const notes = dv.pages('"IndexTTS本地部署[文本转语音]"')
  .where(p => p.file.ext === "md" && p.file.name !== dv.current().file.name && !p.file.path.includes("Templates") && !p.file.tags.includes("moc"))
  .sort(p => p.file.mtime, "desc");

dv.table(["笔记", "标签", "最后修改"], notes.map(p => [
  p.file.link,
  p.file.tags.join(", ") || "—",
  p.file.mtime.toFormat("DD HH:mm")
]));
```

## 🐛 问题日志

- [[问题详述]]
