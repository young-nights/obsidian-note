#!/usr/bin/env python3
"""
早上9点执行：删除广告邮件和HSBC通知邮件
"""

import json
import imaplib
import email
from email_manager import QQEmailManager

# 需要删除的关键词
DELETE_KEYWORDS = {
    "广告": ["广告", "促销", "优惠", "折扣", "免费", "中奖", "抽奖", "限时", "抢购"],
    "HSBC通知": ["登入通知", "登出通知", "登入", "登出", "买入", "卖出", "交易通知"],
    "招聘": ["对您很感兴趣", "邀您沟通", "职位邀请"],
    "其他": ["保值小妙招", "闲置域名", "AI", "start with"]
}

def should_delete(subject, body, from_addr):
    """判断是否应该删除邮件"""
    text = (subject + " " + body + " " + from_addr).lower()
    
    for category, keywords in DELETE_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text:
                return True, category
    
    return False, None

def delete_emails_by_category(account):
    """删除指定类别的邮件"""
    manager = QQEmailManager(account['email'], account['auth_code'])
    
    if not manager.connect_imap():
        print(f"❌ 连接失败: {account['email']}")
        return 0
    
    try:
        manager.imap.select("INBOX")
        status, messages = manager.imap.search(None, "UNSEEN")
        email_ids = messages[0].split()
        
        deleted_count = 0
        categories = {}
        
        for eid in email_ids:
            status, msg_data = manager.imap.fetch(eid, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            
            subject = manager.decode_header(msg["Subject"])
            from_addr = msg["From"]
            body = manager.get_email_body(msg)
            
            should_del, category = should_delete(subject, body, from_addr)
            
            if should_del:
                # 标记为删除
                manager.imap.store(eid, '+FLAGS', '\\Deleted')
                deleted_count += 1
                categories[category] = categories.get(category, 0) + 1
                print(f"  🗑️ 删除: [{category}] {subject[:50]}")
        
        # 执行删除
        if deleted_count > 0:
            manager.imap.expunge()
        
        return deleted_count, categories
        
    except Exception as e:
        print(f"❌ 删除失败: {e}")
        return 0, {}
    finally:
        manager.imap.logout()

def main():
    print("🧹 早上邮件清理")
    print("=" * 40)
    
    with open('/home/node/.openclaw/workspace/skills/email-manager/config.json', 'r') as f:
        config = json.load(f)
    
    total_deleted = 0
    
    for account in config['accounts']:
        print(f"\n📧 处理: {account['email']}")
        deleted, categories = delete_emails_by_category(account)
        total_deleted += deleted
        
        if categories:
            print(f"  ✅ 已删除 {deleted} 封:")
            for cat, count in categories.items():
                print(f"    - {cat}: {count}封")
    
    print(f"\n📊 总计删除: {total_deleted} 封")
    
    # 保存清理日志
    with open('/home/node/.openclaw/workspace/skills/email-manager/cleanup_log.txt', 'a') as f:
        from datetime import datetime
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - 删除 {total_deleted} 封\n")

if __name__ == "__main__":
    main()
