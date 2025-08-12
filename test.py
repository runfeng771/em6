#!/usr/bin/env python3
"""
测试脚本 - 验证自动登录管理系统是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Account, EmailConfig, SchedulerConfig

def test_database():
    """测试数据库连接和初始化"""
    print("测试数据库连接...")
    try:
        with app.app_context():
            # 测试创建表
            db.create_all()
            
            # 测试默认账号
            account_count = Account.query.count()
            print(f"数据库中的账号数量: {account_count}")
            
            # 测试默认邮件配置
            email_config = EmailConfig.query.first()
            if email_config:
                print(f"邮件配置: {email_config.smtp_server}:{email_config.smtp_port}")
            
            # 测试默认调度配置
            scheduler_config = SchedulerConfig.query.first()
            if scheduler_config:
                print(f"调度配置: {scheduler_config.hour1}:{scheduler_config.minute1}, {scheduler_config.hour2}:{scheduler_config.minute2}")
            
            print("✅ 数据库测试通过")
            return True
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

def test_routes():
    """测试主要路由"""
    print("测试路由...")
    try:
        with app.test_client() as client:
            # 测试首页
            response = client.get('/')
            if response.status_code == 200:
                print("✅ 首页路由正常")
            else:
                print(f"❌ 首页路由异常: {response.status_code}")
                return False
            
            # 测试API路由
            response = client.get('/api/accounts')
            if response.status_code == 200:
                print("✅ API路由正常")
            else:
                print(f"❌ API路由异常: {response.status_code}")
                return False
            
            # 测试保活路由
            response = client.get('/api/keep_alive')
            if response.status_code == 200:
                print("✅ 保活路由正常")
            else:
                print(f"❌ 保活路由异常: {response.status_code}")
                return False
            
        print("✅ 路由测试通过")
        return True
    except Exception as e:
        print(f"❌ 路由测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖包"""
    print("测试依赖包...")
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'requests',
        'ddddocr',
        'cryptography',
        'apscheduler'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        return False
    
    print("✅ 依赖包测试通过")
    return True

def main():
    """主测试函数"""
    print("=" * 50)
    print("自动登录管理系统 - 测试脚本")
    print("=" * 50)
    
    tests = [
        ("依赖包", test_dependencies),
        ("数据库", test_database),
        ("路由", test_routes)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name}测试 ---")
        if test_func():
            passed += 1
        print("-" * 30)
    
    print(f"\n测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统可以正常运行。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查配置。")
        return 1

if __name__ == '__main__':
    sys.exit(main())