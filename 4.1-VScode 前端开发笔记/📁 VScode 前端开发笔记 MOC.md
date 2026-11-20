---
tags:
  - moc
  - vscode-frontend
created: 2026-04-05 07:15:52
type: MOC
status: active
folder: VScode 前端开发笔记
---

# <font size=4>📁 VScode 前端开发笔记 MOC</font>

<font size=2>

> **VScode 前端开发笔记** 的内容地图（Map of Content）。一个入口，串联所有相关笔记。

</font>

## <font size=3>📋 概览</font>

<font size=2>

```dataviewjs
const statusMap = { active: "🟢 进行中", planning: "🟡 规划中", archived: "📦 已归档" };
const cur = dv.current();
const noteCount = dv.pages('"VScode 前端开发笔记"')
  .where(p => p.file.ext === "md" && p.file.name !== cur.file.name && !p.file.tags.includes("moc"))
  .length;
dv.table(["属性", "值"], [
  ["状态", statusMap[cur.status] || "❓"],
  ["文件夹", cur.file.folder],
  ["笔记数", noteCount],
  ["创建", cur.file.ctime.toFormat("yyyy年M月d日")]
]);
```

</font>

## <font size=3>⭐ 核心笔记</font>

<font size=2>

<!-- 手动添加最重要、最常查阅的 3~5 篇笔记 -->

- [[VScode前端开发环境搭建]]

</font>

## <font size=3>🗂️ 分类导航</font>

<font size=2>

### 环境搭建

- [[VScode前端开发环境搭建]]

### 开发框架

- 

</font>

## <font size=3>🔗 关联 MOC</font>

<font size=2>

<!-- 链接到其他主题的 MOC，构建知识网络 -->

- 

</font>

## <font size=3>📌 待办 & 下一步</font>

<font size=2>

<!-- 当主题还在进行中时，记录待完成的内容 -->

- [ ] 补充 VSCode 插件推荐
- [ ] 添加 Vite + Svelte 5 项目创建教程
- [ ] 添加 LVGL UI 风格实现指南

</font>

## <font size=3>📚 学习路径</font>

<font size=2>

```dataviewjs
const notes = dv.pages('"VScode 前端开发笔记"')
  .where(p => p.file.ext === "md" && p.file.name !== dv.current().file.name && !p.file.tags.includes("moc"))
  .sort(p => p.file.ctime, "asc");

const levelMap = { "基础": "📗 基础", "进阶": "📘 进阶", "高级": "📕 高级" };

dv.table(["笔记", "难度", "修改"], notes.map(p => {
  const level = p.file.tags.find(t => levelMap[t]);
  return [
    p.file.link,
    level ? levelMap[level] : "📝 其他",
    p.file.mtime.toFormat("DD")
  ];
}));
```

</font>

## <font size=3>🕐 最近修改（7 天内）</font>

<font size=2>

```dataviewjs
const recent = dv.pages('"VScode 前端开发笔记"')
  .where(p =>
    p.file.ext === "md"
    && p.file.name !== dv.current().file.name
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

</font>

## <font size=3>📊 全部笔记</font>

<font size=2>

```dataviewjs
const iconMap = { issue: "🐛", config: "⚙️", guide: "📖" };

const notes = dv.pages('"VScode 前端开发笔记"')
  .where(p => p.file.ext === "md" && p.file.name !== dv.current().file.name && !p.file.tags.includes("moc"))
  .sort(p => p.file.mtime, "desc");

dv.table([" ", "笔记", "标签", "链接数", "修改"], notes.map(p => {
  const icon = p.file.tags.find(t => iconMap[t]);
  return [
    icon ? iconMap[icon] : "📝",
    p.file.link,
    p.file.tags.join(", ") || "—",
    p.file.outlinks.length,
    p.file.mtime.toFormat("DD HH:mm")
  ];
}));
```

</font>

## <font size=3>🏷️ 按标签聚合</font>

<font size=2>

```dataviewjs
const notes = dv.pages('"VScode 前端开发笔记"')
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

</font>

## <font size=3>🐛 问题日志</font>

<font size=2>

<!-- 记录踩过的坑，方便回查 -->

| 日期 | 问题 | 解决方案 | 关联笔记 |
|------|------|----------|----------|
|  |  |  |  |

</font>

---

<font size=2>

> 📝 *本 MOC 由模板自动生成，手动维护核心笔记和关联部分，动态列表由 DataviewJS 驱动。*

</font>
