#!/usr/bin/env python3
"""
晚上10点执行：生成邮箱日报并推送
"""

import json
import sys
import os
from email_manager import QQEmailManager, classify_email
from datetime import datetime

def load_config():
    """加载配置"""
    with open('/home/node/.openclaw/workspace/skills/email-manager/config.json', 'r') as f:
        return json.load(f)

def fetch_and_classify(limit=30):
    """获取并分类邮件"""
    config = load_config()
    results = []
    
    for account in config['accounts']:
        print(f"\n📧 检查邮箱: {account['email']}")
        
        manager = QQEmailManager(account['email'], account['auth_code'])
        emails = manager.get_unread_emails(limit=limit)
        
        classified = {
            "🔴 紧急": [],
            "🟡 重要": [],
            "🔵 订阅": [],
            "⚪ 垃圾": []
        }
        
        for email_data in emails:
            category = classify_email(
                email_data['subject'],
                email_data['body'],
                email_data['from']
            )
            classified[category].append(email_data)
        
        results.append({
            "account": account['email'],
            "emails": classified
        })
    
    return results

def generate_report(results):
    """生成邮箱日报"""
    report = []
    report.append("📬 晚间邮箱日报")
    report.append(f"📅 {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
    report.append("")
    
    total_urgent = 0
    total_important = 0
    total_subscription = 0
    total_spam = 0
    
    for result in results:
        report.append(f"📧 {result['account']}")
        
        for category, emails in result['emails'].items():
            count = len(emails)
            if count == 0:
                continue
            
            if category == "🔴 紧急":
                total_urgent += count
            elif category == "🟡 重要":
                total_important += count
            elif category == "🔵 订阅":
                total_subscription += count
            elif category == "⚪ 垃圾":
                total_spam += count
            
            report.append(f"{category} ({count}封)")
            
            for email_data in emails:
                subject = email_data['subject'][:40]
                from_addr = email_data['from'][:25]
                report.append(f"  • [{from_addr}] {subject}")
        
        report.append("")
    
    report.append("📊 统计")
    report.append(f"  紧急: {total_urgent} 封")
    report.append(f"  重要: {total_important} 封")
    report.append(f"  订阅: {total_subscription} 封")
    report.append(f"  垃圾: {total_spam} 封")
    
    return "\n".join(report)

def main():
    print("📬 生成晚间邮箱日报...")
    
    results = fetch_and_classify(limit=30)
    report = generate_report(results)
    
    # 保存报告
    report_path = '/home/node/.openclaw/workspace/skills/email-manager/daily_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 输出报告内容（用于cron任务的announce）
    print("\n" + "=" * 50)
    print(report)
    print("=" * 50)
    
    print(f"\n✅ 日报已保存到: {report_path}")
    
    return report

if __name__ == "__main__":
    main()
