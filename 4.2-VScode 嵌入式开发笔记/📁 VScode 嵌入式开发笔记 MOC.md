---
tags:
  - moc
  - index
  - vscode-embedded
created: 2026-04-05 07:15:52
type: MOC
status: active
folder: VScode 嵌入式开发笔记
---

# <font size=4>📁 VScode 嵌入式开发笔记 MOC</font>

<font size=2>

> **VScode 嵌入式开发笔记** 的内容地图（Map of Content）。一个入口，串联所有相关笔记。

</font>

## <font size=3>📋 概览</font>

<font size=2>

```dataviewjs
const statusMap = { active: "🟢 进行中", planning: "🟡 规划中", archived: "📦 已归档" };
const cur = dv.current();
const noteCount = dv.pages('"VScode 嵌入式开发笔记"')
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

- [[VScode嵌入式开发环境搭建]]

</font>

## <font size=3>🗂️ 分类导航</font>

<font size=2>

### 环境搭建

- [[VScode嵌入式开发环境搭建]]

### 构建与调试

- 

</font>

## <font size=3>🔗 关联 MOC</font>

<font size=2>

<!-- 链接到其他主题的 MOC，构建知识网络 -->

- [[📁 VScode 前端开发笔记 MOC]]

</font>

## <font size=3>📌 待办 & 下一步</font>

<font size=2>

<!-- 当主题还在进行中时，记录待完成的内容 -->

- [x] 补充 VSCode 插件推荐（2026-11-13 已完成插件扫描）
- [x] 记录 CMake 编译流程（2026-11-13 实测通过）
- [ ] 补充 sensor / remote 板 CMake 补丁差异核对
- [ ] 添加 Cortex-Debug + ST-Link 调试配置（launch.json）教程
- [ ] 添加 Keil / EIDE 构建路线教程

</font>

## <font size=3>📚 学习路径</font>

<font size=2>

```dataviewjs
const notes = dv.pages('"VScode 嵌入式开发笔记"')
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
const recent = dv.pages('"VScode 嵌入式开发笔记"')
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

const notes = dv.pages('"VScode 嵌入式开发笔记"')
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
const notes = dv.pages('"VScode 嵌入式开发笔记"')
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
| 2026-11-13 | scons 4.11 报 `deque + list` TypeError | 锁定 `pip install scons==4.4.0` | [[VScode嵌入式开发环境搭建]] |
| 2026-11-13 | `scons --target=cmake` 假编译输出无产物 | dry-run 属正常，真正构建走 CMake Tools | [[VScode嵌入式开发环境搭建]] |
| 2026-11-13 | 生成的 CMakeLists.txt 缺 HAL 头 / 源 | 按 Debug/makefile 追加补丁段 | [[VScode嵌入式开发环境搭建]] |
| 2026-11-13 | scons 报 Cannot found toolchain directory | 设置 `RTT_EXEC_PATH` 指向 gcc bin 目录 | [[VScode嵌入式开发环境搭建]] |

</font>

---

<font size=2>

> 📝 *本 MOC 由模板自动生成，手动维护核心笔记和关联部分，动态列表由 DataviewJS 驱动。*

</font>
