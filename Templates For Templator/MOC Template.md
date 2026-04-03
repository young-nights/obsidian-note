<%*
// ============================================================
//  MOC Template v2 — 全面升级版（DataviewJS）
// ============================================================

// === 自动获取当前文件夹名 ===
const folderPath = tp.file.folder(true);
const suggestedName = folderPath.split('/').pop() || tp.file.title;

// === 用户输入 ===
let mocName = await tp.system.prompt("MOC 名称（自动建议文件夹名）", suggestedName);
if (!mocName) mocName = suggestedName;

let emoji = await tp.system.prompt("开头 Emoji（回车默认 📁）", "📁");
if (!emoji) emoji = "📁";

let status = await tp.system.prompt("项目状态：planning / active / archived", "active");

let categoryInput = await tp.system.prompt("自定义分类（逗号分隔，回车跳过使用默认）", "");

// 解析分类
let categories = categoryInput
  ? categoryInput.split(/[,，]/).map(s => s.trim()).filter(Boolean)
  : ["核心笔记", "环境与配置", "问题与排错", "参考资源"];

// 自动重命名
await tp.file.rename((emoji ? emoji + " " : "") + mocName + " MOC");
%>

---
tags: [moc, index, <%* mocName.toLowerCase().replace(/ /g, '-') %>]
created: <% tp.date.now("YYYY-MM-DD HH:mm:ss") %>
type: MOC
status: <% status %>
folder: "<%* folderPath %>"
---

# <% tp.file.title %>

> **<% mocName %>** 的内容地图（Map of Content）。一个入口，串联所有相关笔记。

## 📋 概览

```dataviewjs
const statusMap = { active: "🟢 进行中", planning: "🟡 规划中", archived: "📦 已归档" };
const cur = dv.current();
const noteCount = dv.pages('"<%* folderPath %>"')
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

-

## 🗂️ 分类导航

<%* for (const cat of categories) { -%>
### <% cat %>

-
<%* } -%>

## 🔗 关联 MOC
<!-- 链接到其他主题的 MOC，构建知识网络 -->

-

## 📌 待办 & 下一步
<!-- 当主题还在进行中时，记录待完成的内容 -->

- [ ] 

## 📚 学习路径

```dataviewjs
const notes = dv.pages('"<%* folderPath %>"')
  .where(p => p.file.ext === "md" && p.file.name !== dv.current().file.name && !p.file.path.includes("Templates") && !p.file.tags.includes("moc"))
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

## 🕐 最近修改（7 天内）

```dataviewjs
const recent = dv.pages('"<%* folderPath %>"')
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

## 📊 全部笔记

```dataviewjs
const iconMap = { issue: "🐛", config: "⚙️", guide: "📖" };

const notes = dv.pages('"<%* folderPath %>"')
  .where(p => p.file.ext === "md" && p.file.name !== dv.current().file.name && !p.file.path.includes("Templates") && !p.file.tags.includes("moc"))
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

## 🏷️ 按标签聚合

```dataviewjs
const notes = dv.pages('"<%* folderPath %>"')
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
