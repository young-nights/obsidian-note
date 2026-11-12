---
name: email-manager
description: Manage emails with intelligent triage, summarization, and drafting. Use when: user asks to check emails, process inbox, summarize emails, classify emails, draft replies, or any email-related tasks. Covers email reading, categorization (urgent/important/subscription/spam), summarization, draft creation, and notification.
---

# Email Manager

Personal email management skill for intelligent triage and processing.

## Quick Start

```bash
# 获取邮件并生成日报
cd /home/node/.openclaw/workspace/skills/email-manager
python3 fetch_emails.py [数量]

# 测试邮箱连接
python3 -c "from email_manager import QQEmailManager; print('OK')"
```

## Core Workflow

1. **Fetch** → Retrieve new/unread emails
2. **Classify** → Categorize each email
3. **Summarize** → Generate concise summaries
4. **Action** → Draft replies, archive, delete, or flag

## Email Classification

Categorize each email into one of four tiers:

| Category | Priority | Action |
|----------|----------|--------|
| 🔴 紧急 | Immediate attention required | Flag + notify user |
| 🟡 重要 | Needs response within 24h | Summary + draft suggestion |
| 🔵 订阅 | Newsletters, notifications | Batch summary |
| ⚪ 垃圾 | Spam, ads, promotions | Auto-archive/delete |

## Files

- `config.json` - 邮箱账号配置
- `email_manager.py` - 核心邮件访问类
- `fetch_emails.py` - 邮件获取与分类脚本
- `latest_report.txt` - 最新生成的日报

## Processing Format

When processing emails, output in this format:

```
## 📬 邮箱日报

### 🔴 紧急 (X封)
- [发件人] 主题 → 建议行动

### 🟡 重要 (X封)
- [发件人] 主题 → 摘要

### 🔵 订阅 (X封)
- 已处理 X 封，跳过

### ⚪ 垃圾 (X封)
- 已删除 X 封
```

## Summarization Rules

- Single email: 1-2 sentence summary
- Thread: Key points + latest status
- Newsletter: Extract actionable items only

## Draft Guidelines

- Match user's communication style (concise, professional)
- Chinese by default, switch if sender uses English
- Never send without user confirmation
- Save drafts for review, not auto-send

## Safety

- Never auto-delete without classification confirmation
- Preserve all attachments references
- Log all actions for audit trail
- High-risk emails (financial, legal) always require user review
- 授权码存储在 config.json 中，注意保护隐私
