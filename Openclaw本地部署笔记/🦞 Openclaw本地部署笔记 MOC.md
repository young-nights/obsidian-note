---
tags:
  - moc
  - openclaw
created: 2026-04-02 03:30:22
type: MOC
status: active
folder: Openclaw本地部署笔记
---
# <font size=4>🦞 Openclaw 本地部署笔记 MOC</font>

> **Openclaw本地部署笔记** 的内容地图（Map of Content）。一个入口，串联所有相关笔记。

## 📋 概览

```dataviewjs
const statusMap = { active: "🟢 进行中", planning: "🟡 规划中", archived: "📦 已归档" };
const cur = dv.current();
const noteCount = dv.pages('"Openclaw本地部署笔记"')
  .where(p => p.file.ext === "md" && p.file.name !== cur.file.name && !p.file.path.includes("Templates"))
  .length;
dv.table(["属性", "值"], [
  ["状态", statusMap[cur.status] || "❓"],
  ["文件夹", cur.file.folder],
  ["笔记数", noteCount],
  ["创建", cur.file.ctime.toFormat("yyyy年M月d日")]
]);
```

## ⭐ 核心笔记
<!-- 手动添加最重要、最常查阅的 3~5 篇笔记 -->

- [[Windows+WSL+Ubuntu本地部署]]
- [[Ubuntu-server-OpenClaw本地部署]]
- [[Windows Docker Desktop+WSL+Ubuntu本地部署]]
- [[Ubuntu-desktop-OpenClaw本地部署]]

## 🗂️ 分类导航

### 参考资源

- [OpenClaw 官方仓库](https://github.com/openclaw/openclaw)
- [Docker Compose releases](https://github.com/docker/compose/releases)

## 🔗 关联 MOC
<!-- 链接到其他主题的 MOC，构建知识网络 -->

- [[🐧 Linux 笔记 MOC]] — Linux 基础操作与系统管理
- [[🖥️ Ubuntu-Server MOC]] — Ubuntu Server 配置专题

## 📌 待办 & 下一步
<!-- 当主题还在进行中时，记录待完成的内容 -->

- [ ] 补充常见问题排查文档


## 🕐 最近修改（7 天内）

```dataviewjs
const recent = dv.pages('"Openclaw本地部署笔记"')
  .where(p =>
    p.file.ext === "md"
    && p.file.name !== dv.current().file.name
    && !p.file.path.includes("Templates")
    && !p.file.tags.includes("moc")
    && p.file.mtime >= dv.date("today").minus(dv.duration("7 days"))
  )
  .sort(p => p.file.mtime, "desc")
  .limit(10);

dv.table(["笔记", "标签", "修改时间"], recent.map(p => [
  p.file.link,
  p.file.tags.join(", ") || "—",
  p.file.mtime.toFormat("DD HH:mm")
]));
```


## 🏷️ 按标签聚合

```dataviewjs
const notes = dv.pages('"Openclaw本地部署笔记"')
  .where(p => p.file.ext === "md" && p.file.tags.length > 0 && !p.file.tags.includes("moc"));

const tagGroups = {};
for (const p of notes) {
  for (const tag of p.file.tags) {
    if (!tagGroups[tag]) tagGroups[tag] = [];
    tagGroups[tag].push(p.file.link);
  }
}

const rows = Object.entries(tagGroups)
  .sort((a, b) => b[1].length - a[1].length);

dv.table(["标签", "笔记数", "包含笔记"], rows.map(([tag, links]) => [
  tag,
  links.length,
  links.join(", ")
]));
```

## 🐛 问题日志
<!-- 记录踩过的坑，方便回查 -->

| 日期 | 问题 | 解决方案 | 关联笔记 |
|------|------|----------|----------|
|  |  |  |  |

---

> 📝 *本 MOC 由模板自动生成，手动维护核心笔记和关联部分，动态列表由 DataviewJS 驱动。*
