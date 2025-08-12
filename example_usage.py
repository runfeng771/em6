#!/usr/bin/env python3
"""
使用示例脚本 - 演示如何使用自动登录管理系统的API
"""

import requests
import json
import time

class AutoLoginClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def test_connection(self):
        """测试连接"""
        try:
            response = requests.get(f"{self.base_url}/api/keep_alive")
            if response.status_code == 200:
                print("✅ 连接成功")
                return True
            else:
                print(f"❌ 连接失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 连接异常: {e}")
            return False
    
    def add_account(self, name, email, password):
        """添加账号"""
        data = {
            "name": name,
            "account": email,
            "password": password
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/accounts", json=data)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 账号添加成功: {result['account']['name']}")
                return result['account']['id']
            else:
                print(f"❌ 账号添加失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 添加账号异常: {e}")
            return None
    
    def get_accounts(self):
        """获取所有账号"""
        try:
            response = requests.get(f"{self.base_url}/api/accounts")
            if response.status_code == 200:
                accounts = response.json()
                print(f"✅ 获取到 {len(accounts)} 个账号")
                return accounts
            else:
                print(f"❌ 获取账号失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ 获取账号异常: {e}")
            return []
    
    def manual_login(self, account_id):
        """手动登录"""
        try:
            response = requests.post(f"{self.base_url}/api/accounts/{account_id}/login")
            if response.status_code == 200:
                print(f"✅ 登录任务已启动，账号ID: {account_id}")
                return True
            else:
                print(f"❌ 登录任务启动失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False
    
    def get_logs(self, date=None, account=None, level=None):
        """获取日志"""
        params = {}
        if date:
            params['date'] = date
        if account:
            params['account'] = account
        if level:
            params['level'] = level
        
        try:
            response = requests.get(f"{self.base_url}/api/logs", params=params)
            if response.status_code == 200:
                logs_data = response.json()
                print(f"✅ 获取到 {logs_data['total']} 条日志")
                return logs_data
            else:
                print(f"❌ 获取日志失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 获取日志异常: {e}")
            return None
    
    def get_email_config(self):
        """获取邮件配置"""
        try:
            response = requests.get(f"{self.base_url}/api/email_config")
            if response.status_code == 200:
                config = response.json()
                print("✅ 获取邮件配置成功")
                return config
            else:
                print(f"❌ 获取邮件配置失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 获取邮件配置异常: {e}")
            return None
    
    def update_email_config(self, smtp_server, smtp_port, sender_email, sender_password, receiver_email, is_active=True):
        """更新邮件配置"""
        data = {
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "sender_email": sender_email,
            "sender_password": sender_password,
            "receiver_email": receiver_email,
            "is_active": is_active
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/email_config", json=data)
            if response.status_code == 200:
                print("✅ 邮件配置更新成功")
                return True
            else:
                print(f"❌ 邮件配置更新失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 更新邮件配置异常: {e}")
            return False
    
    def get_scheduler_config(self):
        """获取定时任务配置"""
        try:
            response = requests.get(f"{self.base_url}/api/scheduler_config")
            if response.status_code == 200:
                config = response.json()
                print("✅ 获取定时任务配置成功")
                return config
            else:
                print(f"❌ 获取定时任务配置失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 获取定时任务配置异常: {e}")
            return None
    
    def update_scheduler_config(self, hour1, minute1, hour2, minute2, is_enabled=True):
        """更新定时任务配置"""
        data = {
            "hour1": hour1,
            "minute1": minute1,
            "hour2": hour2,
            "minute2": minute2,
            "is_enabled": is_enabled
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/scheduler_config", json=data)
            if response.status_code == 200:
                print("✅ 定时任务配置更新成功")
                return True
            else:
                print(f"❌ 定时任务配置更新失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 更新定时任务配置异常: {e}")
            return False
    
    def clear_logs(self, date=None):
        """清空日志"""
        data = {}
        if date:
            data['date'] = date
        
        try:
            response = requests.post(f"{self.base_url}/api/logs/clear", json=data)
            if response.status_code == 200:
                print("✅ 日志清空成功")
                return True
            else:
                print(f"❌ 日志清空失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 清空日志异常: {e}")
            return False

def main():
    """主函数 - 演示API使用"""
    print("=" * 60)
    print("自动登录管理系统 - API使用示例")
    print("=" * 60)
    
    # 创建客户端
    client = AutoLoginClient()
    
    # 测试连接
    print("\n1. 测试连接...")
    if not client.test_connection():
        print("请确保Flask应用正在运行在 http://localhost:5000")
        return
    
    # 获取现有账号
    print("\n2. 获取现有账号...")
    accounts = client.get_accounts()
    
    # 添加测试账号
    print("\n3. 添加测试账号...")
    test_account_id = client.add_account(
        name="测试账号",
        email="test@example.com",
        password="test123"
    )
    
    # 再次获取账号
    print("\n4. 再次获取账号...")
    accounts = client.get_accounts()
    
    # 手动登录
    if test_account_id:
        print("\n5. 手动登录测试...")
        client.manual_login(test_account_id)
    
    # 等待一段时间
    print("\n6. 等待登录完成...")
    time.sleep(10)
    
    # 获取日志
    print("\n7. 获取日志...")
    logs = client.get_logs()
    
    # 获取邮件配置
    print("\n8. 获取邮件配置...")
    email_config = client.get_email_config()
    
    # 获取定时任务配置
    print("\n9. 获取定时任务配置...")
    scheduler_config = client.get_scheduler_config()
    
    # 更新定时任务配置
    if scheduler_config:
        print("\n10. 更新定时任务配置...")
        client.update_scheduler_config(
            hour1=10,
            minute1=0,
            hour2=14,
            minute2=30,
            is_enabled=True
        )
    
    # 清空今天的日志
    print("\n11. 清空日志...")
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    client.clear_logs(today)
    
    print("\n" + "=" * 60)
    print("API使用示例完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()