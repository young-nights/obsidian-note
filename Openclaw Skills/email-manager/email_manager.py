#!/usr/bin/env python3
"""
Email Manager - QQ邮箱访问工具
支持IMAP读取和SMTP发送
"""

import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import os

class QQEmailManager:
    def __init__(self, email_addr, auth_code):
        self.email_addr = email_addr
        self.auth_code = auth_code
        self.imap_server = "imap.qq.com"
        self.smtp_server = "smtp.qq.com"
        self.imap_port = 993
        self.smtp_port = 465
        
    def connect_imap(self):
        """连接IMAP服务器"""
        try:
            self.imap = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.imap.login(self.email_addr, self.auth_code)
            return True
        except Exception as e:
            print(f"IMAP连接失败: {e}")
            return False
    
    def connect_smtp(self):
        """连接SMTP服务器"""
        try:
            self.smtp = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            self.smtp.login(self.email_addr, self.auth_code)
            return True
        except Exception as e:
            print(f"SMTP连接失败: {e}")
            return False
    
    def get_unread_emails(self, folder="INBOX", limit=20):
        """获取未读邮件"""
        if not self.connect_imap():
            return []
        
        try:
            self.imap.select(folder)
            status, messages = self.imap.search(None, "UNSEEN")
            email_ids = messages[0].split()
            
            emails = []
            for eid in email_ids[-limit:]:  # 最近的N封
                status, msg_data = self.imap.fetch(eid, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                
                # 解析邮件内容
                subject = self.decode_header(msg["Subject"])
                from_addr = msg["From"]
                date = msg["Date"]
                body = self.get_email_body(msg)
                
                emails.append({
                    "id": eid.decode(),
                    "subject": subject,
                    "from": from_addr,
                    "date": date,
                    "body": body[:500] if body else ""  # 只取前500字符
                })
            
            return emails
        except Exception as e:
            print(f"获取邮件失败: {e}")
            return []
        finally:
            self.imap.logout()
    
    def decode_header(self, header):
        """解码邮件头"""
        if header is None:
            return ""
        decoded = email.header.decode_header(header)
        result = ""
        for content, charset in decoded:
            if isinstance(content, bytes):
                result += content.decode(charset or "utf-8", errors="ignore")
            else:
                result += content
        return result
    
    def get_email_body(self, msg):
        """提取邮件正文"""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        return payload.decode("utf-8", errors="ignore")
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                return payload.decode("utf-8", errors="ignore")
        return ""
    
    def send_email(self, to_addr, subject, body, html=False):
        """发送邮件"""
        if not self.connect_smtp():
            return False
        
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_addr
            msg["To"] = to_addr
            msg["Subject"] = subject
            
            if html:
                msg.attach(MIMEText(body, "html", "utf-8"))
            else:
                msg.attach(MIMEText(body, "plain", "utf-8"))
            
            self.smtp.send_message(msg)
            return True
        except Exception as e:
            print(f"发送邮件失败: {e}")
            return False
        finally:
            self.smtp.quit()
    
    def get_recent_emails(self, folder="INBOX", days=1, limit=50):
        """获取最近N天的邮件"""
        if not self.connect_imap():
            return []
        
        try:
            self.imap.select(folder)
            # 搜索最近N天的邮件
            date = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
            status, messages = self.imap.search(None, f'(SINCE "{date}")')
            email_ids = messages[0].split()
            
            emails = []
            for eid in email_ids[-limit:]:
                status, msg_data = self.imap.fetch(eid, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                
                subject = self.decode_header(msg["Subject"])
                from_addr = msg["From"]
                date_str = msg["Date"]
                body = self.get_email_body(msg)
                
                emails.append({
                    "id": eid.decode(),
                    "subject": subject,
                    "from": from_addr,
                    "date": date_str,
                    "body": body[:500] if body else ""
                })
            
            return emails
        except Exception as e:
            print(f"获取邮件失败: {e}")
            return []
        finally:
            self.imap.logout()

def classify_email(subject, body, from_addr):
    """简单邮件分类"""
    # 紧急关键词
    urgent_keywords = ["紧急", "urgent", "重要通知", "立即", "asap", "critical"]
    # 重要关键词
    important_keywords = ["会议", "合同", "付款", "发票", "会议", "审批", "deadline"]
    # 订阅关键词
    subscription_keywords = ["订阅", "newsletter", "weekly", "daily", "update", "通知"]
    # 垃圾关键词
    spam_keywords = ["广告", "促销", "优惠", "折扣", "免费", "中奖", "抽奖"]
    
    text = (subject + " " + body).lower()
    
    for kw in urgent_keywords:
        if kw in text:
            return "🔴 紧急"
    
    for kw in important_keywords:
        if kw in text:
            return "🟡 重要"
    
    for kw in subscription_keywords:
        if kw in text:
            return "🔵 订阅"
    
    for kw in spam_keywords:
        if kw in text:
            return "⚪ 垃圾"
    
    return "🟡 重要"  # 默认归类为重要

if __name__ == "__main__":
    # 测试代码
    print("Email Manager - QQ邮箱工具已加载")
