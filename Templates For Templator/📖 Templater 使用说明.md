# Templater 使用说明

## 插件简介

Templater 是 Obsidian 社区插件中功能最强的模板引擎。相比官方核心插件 Templates，它支持 **JavaScript 脚本执行**、**用户交互（弹窗输入/选择）** 和 **文件系统操作**，能将模板从静态文本升级为动态自动化工具。

核心能力：
- 用 `<% %>` / `<%* %>` 嵌入 JS 表达式和逻辑
- 通过 `tp.*` 系列 API 读取文件信息、触发用户交互
- 支持绑定 hotkey 一键插入模板、自动文件夹模板（Folder Templates）

## 安装与配置

### 安装步骤

1. 打开 Obsidian → **Settings → Community plugins → Browse**
2. 搜索 **Templater**，点击 Install → Enable
3. （可选）禁用官方 Templates 插件以避免冲突

### 核心设置项

进入 **Settings → Templater**：

| 设置项 | 说明 |
|--------|------|
| **Template folder location** | 模板文件夹路径，如 `Templates/Templater` |
| **Trigger Templater on new file creation** | 开启后，新建笔记时自动替换模板语法 |
| **Automatic jump to cursor** | 插入模板后光标自动跳到 `<% tp.file.cursor() %>` 位置 |
| **Folder Templates** | 指定文件夹 → 自动关联模板（免手动插入） |

> [!tip] 建议
> 开启 **Trigger on new file creation** + 配置 **Folder Templates**，这样在指定文件夹新建笔记就会自动生成内容，无需手动操作。

## 模板语法基础

### `<% %>` — 输出表达式

用于**输出值**，不执行复杂逻辑：

```
今天是 <% tp.date.now("YYYY-MM-DD") %>
当前笔记: <% tp.file.title %>
```

### `<%* %>` — 执行脚本

用于**执行 JavaScript 代码**，可以写 if/for/let 等：

```
<%*
let name = await tp.system.prompt("请输入姓名");
let greet = name ? `你好，${name}！` : "你好！";
-%>
<% greet %>
```

> [!info] 关键区别
> - `<% %>` = 输出表达式结果（类似 `console.log`）
> - `<%* %>` = 执行代码块（类似 script 标签）
> - `<%* -%>` 中的 `-` 会**去除该行产生的空白行**

### `tp.file` 对象

提供当前文件的元信息：

| 属性 / 方法 | 说明 |
|-------------|------|
| `tp.file.title` | 当前文件名（不含扩展名） |
| `tp.file.folder(relative)` | 所在文件夹路径，`relative` 为 true 时返回相对 vault 根目录的路径 |
| `tp.file.path(relative)` | 完整路径 |
| `tp.file.cursor(n)` | 设置光标占位，n 为序号 |
| `tp.file.rename(new_name)` | 重命名当前文件 |
| `tp.file.create_new(template, filename, open, folder)` | 创建新笔记 |
| `tp.file.include("[[link]]")` | 插入另一篇笔记的内容 |

### `tp.system` 对象

提供用户交互能力：

| 方法 | 说明 |
|------|------|
| `tp.system.prompt(msg, default)` | 弹窗让用户输入文本 |
| `tp.system.suggester(list_items, items, throw_on_cancel)` | 弹窗让用户从列表中选择 |
| `tp.system.prompt_suggester(msg, list, items)` | prompt + suggester 结合 |
| `tp.system.vault_file_exists(path)` | 检查文件是否存在 |

## 常用 API 速查

### 日期时间 — `tp.date`

```js
tp.date.now("YYYY-MM-DD")          // → 2026-04-02
tp.date.now("dddd, MMMM D")        // → Thursday, April 2
tp.date.now("YYYY-MM-DD", 7)       // 7天后
tp.date.weekday("dddd", 1)         // 本周一
tp.date.tomorrow("YYYY-MM-DD")     // 明天
```

### 文件操作 — `tp.file`

```js
// 获取文件夹路径
tp.file.folder(true)   // → "Projects/2026"

// 重命名（通常放在模板顶部）
tp.file.rename("新名称")

// 按日期自动命名
tp.file.rename(tp.date.now("YYYYMMDD") + " - " + await tp.system.prompt("标题？"))
```

### 用户交互 — `tp.system`

```js
// 文本输入
let title = await tp.system.prompt("笔记标题？", "默认值");

// 列表选择
let status = await tp.system.suggester(
    ["📝 草稿", "✅ 已完成", "🗑️ 归档"],   // 显示文本
    ["Draft", "Done", "Archived"]            // 实际值
);
```

### 杂项

```js
tp.web.random_picture_url()          // 随机图片 URL
tp.file.cursor()                     // 光标最终位置
tp.file.cursor(1)                    // 第一个光标位（跳转顺序）
```

## 实用示例

### 示例 1：每日笔记模板

```markdown
# <% tp.date.now("YYYY年MM月DD日 dddd") %>

## 今日任务
- [ ] 

## 日志
<% tp.file.cursor() %>

## 链接
- [[<% tp.date.now("YYYY-MM-DD", -1) %>]] ← 昨天
- [[<% tp.date.now("YYYY-MM-DD", 1) %>]] → 明天
```

### 示例 2：交互式笔记创建

```markdown
<%*
let title = await tp.system.prompt("笔记标题");
let category = await tp.system.suggester(
    ["📚 学习", "💼 工作", "💡 灵感"],
    ["学习", "工作", "灵感"]
);
await tp.file.rename(title);
-%>
# <% title %>
分类: <% category %>
创建时间: <% tp.date.now("YYYY-MM-DD HH:mm") %>

<% tp.file.cursor() %>
```

### 示例 3：文件夹模板 — 自动命名

搭配 Folder Templates 使用，在 `日记/` 文件夹下新建笔记自动填充：

```markdown
<%*
let dateStr = tp.date.now("YYYY-MM-DD");
await tp.file.rename(dateStr);
-%>
# 日记 <% dateStr %>

## 心情
- 😊 😐 😢

## 内容
<% tp.file.cursor() %>
```

> [!tip] Folder Templates 配置
> Settings → Templater → Folder Templates → 添加映射：`日记` → `Templates/Templater/日记模板`

## 与 Dataview 配合使用

Templater 负责**生成 frontmatter 和结构**，Dataview 负责**查询和展示**，两者是黄金搭档。

### 在模板中写 Dataview 友好的 frontmatter

```markdown
<%*
let project = await tp.system.prompt("项目名");
let status = await tp.system.suggester(
    ["进行中", "已完成", "暂停"],
    ["active", "done", "paused"]
);
-%>
---
project: <% project %>
status: <% status %>
created: <% tp.date.now("YYYY-MM-DD") %>
tags: [project]
---

# <% project %>
<% tp.file.cursor() %>
```

然后用 Dataview 查询：

````markdown
```dataview
TABLE status, created
FROM #project
SORT created DESC
```
````

### 在 Dataviewjs 中引用 Templater 变量

如果你的模板通过 `let` 定义了变量，它们只在模板执行时存在，**不会传递给 Dataview**。正确做法是把值写入 frontmatter 或正文，然后 Dataview 读取这些字段。

> [!warning] 注意
> Templater 的 JS 变量是**运行时临时**的，不能直接被 Dataview 访问。必须通过写入笔记内容（通常是 YAML frontmatter）来桥接。

### Inline Dataview + Templater

在模板中嵌入 inline dataview 查询：

```markdown
项目总数: `= length(file.inlinks)`
```

## 常见问题与排错

### 模板插入后语法没被替换

**症状**：插入后仍显示 `<% tp.date.now(...) %>` 原样文本。

**排查**：
1. 确认插件已启用
2. 检查是否开启了 **Trigger Templater on new file creation**
3. 手动触发：Command Palette → **Templater: Replace templates in the active file**

### `<%* %>` 中报错 "tp is not defined"

**原因**：在纯 `<% %>` 块中写了赋值语句（let/const/var）。

**解决**：赋值和控制流必须用 `<%* %>`（带星号），`<% %>` 只用于输出表达式。

### 模板插入后多出空行

**解决**：在 `<%*` 后加 `-`，变成 `<%* -%>`，会去除该块产生的前后空白。

```
<%* -%>
let x = 1;
-%>
```

### Folder Templates 不生效

**排查**：
1. 确认文件夹路径精确匹配（区分大小写）
2. 新建的是 **空白笔记** 后移入文件夹？→ 必须**在目标文件夹内直接创建**
3. 检查模板路径是否正确（相对 vault 根目录）

### 与 QuickAdd 冲突

如果同时使用 QuickAdd，注意两者都可能监听文件创建事件。建议只保留一个处理自动模板，或明确分工。

---

> [!info] 参考资源
> - 官方文档：https://silentvoid13.github.io/Templater/
> - GitHub：https://github.com/SilentVoid13/Templater
