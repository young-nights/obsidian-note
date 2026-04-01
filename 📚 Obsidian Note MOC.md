---
tags:
  - moc
created: 2026-04-01 17:02:00
type: MOC
status: active
folder: "null"
---

# 📚 Obsidian Note 总入口

> 本知识库的根级索引。一个入口，串联所有主题 MOC。

## 🗂️ 主题地图

```dataviewjs
const statusMap = {
  active: "🟢 进行中",
  planning: "🟡 规划中",
  archived: "📦 已归档"
};

const mocs = dv.pages('""')
  .where(p => p.type === "MOC" && p.file.name !== dv.current().file.name && !p.file.path.includes("Templates"))
  .sort(p => p.status, "asc")
  .sort(p => p.file.mtime, "desc");

dv.table(["MOC", "状态", "链接数", "最后修改"], mocs.map(p => [
  p.file.link,
  statusMap[p.status] || "❓",
  p.file.outlinks.length,
  p.file.mtime.toFormat("DD")
]));
```

## 🕐 全库最近修改（7 天）

```dataviewjs
const folderIcon = (folder) => {
  if (folder.includes("IndexTTS-2")) return "🎙️";
  if (folder.includes("IndexTTS")) return "🎙️";
  if (folder.includes("Linux")) return "🐧";
  if (folder.includes("Ubuntu")) return "🖥️";
  return "📝";
};

const recent = dv.pages('""')
  .where(p =>
    p.file.ext === "md"
    && !p.file.path.includes("Templates")
    && !p.file.tags.includes("moc")
    && !p.file.path.includes(".obsidian")
    && p.file.mtime >= dv.date("today").minus(dv.duration("7 days"))
  )
  .sort(p => p.file.mtime, "desc")
  .limit(15);

dv.table(["笔记", "主题", "修改时间"], recent.map(p => [
  p.file.link,
  folderIcon(p.file.folder),
  p.file.mtime.toFormat("DD HH:mm")
]));
```

## 📊 全库统计

```dataviewjs
const notes = dv.pages('""')
  .where(p =>
    p.file.ext === "md"
    && !p.file.path.includes("Templates")
    && !p.file.tags.includes("moc")
    && !p.file.path.includes(".obsidian")
  );

const folderMap = {};
for (const p of notes) {
  const f = p.file.folder || "(根目录)";
  if (!folderMap[f]) folderMap[f] = 0;
  folderMap[f]++;
}

const rows = Object.entries(folderMap).sort((a, b) => b[1] - a[1]);
dv.table(["文件夹", "笔记数"], rows);
```

---

> 从这里出发，点击任意主题 MOC 开始探索。
