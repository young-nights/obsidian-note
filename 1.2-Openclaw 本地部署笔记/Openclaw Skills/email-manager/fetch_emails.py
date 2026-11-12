#!/usr/bin/env python3
"""
邮件获取与分类脚本
"""

import json
import sys
from email_manager import QQEmailManager, classify_email
from datetime import datetime

def load_config():
    """加载配置"""
    with open('/home/whites/.openclaw/workspace/skills/email-manager/config.json', 'r') as f:
        return json.load(f)

def fetch_and_classify(limit=20):
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
    report.append("## 📬 邮箱日报")
    report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    
    total_urgent = 0
    total_important = 0
    
    for result in results:
        report.append(f"### 📧 {result['account']}")
        
        for category, emails in result['emails'].items():
            count = len(emails)
            if count == 0:
                continue
            
            report.append(f"\n{category} ({count}封)")
            
            for email_data in emails:
                subject = email_data['subject'][:50]
                from_addr = email_data['from'][:30]
                report.append(f"- [{from_addr}] {subject}")
                
                if category == "🔴 紧急":
                    total_urgent += 1
                elif category == "🟡 重要":
                    total_important += 1
        
        report.append("")
    
    report.append(f"\n📊 统计: 紧急 {total_urgent} 封, 重要 {total_important} 封")
    
    return "\n".join(report)

if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    
    print("正在获取邮件...")
    results = fetch_and_classify(limit)
    
    report = generate_report(results)
    print("\n" + report)
    
    # 保存报告
    with open('/home/whites/.openclaw/workspace/skills/email-manager/latest_report.txt', 'w') as f:
        f.write(report)
    
    print("\n✅ 报告已保存到 latest_report.txt")
