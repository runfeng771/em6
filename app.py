from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
import threading
import time
import logging
import os
from werkzeug.security import generate_password_hash, check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import json
import base64
import ddddocr
import requests
import re
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from functools import wraps

app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auto_login.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建必要的目录
os.makedirs('logs', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('static/images', exist_ok=True)

# 数据库模型
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    login_status = db.Column(db.String(20), default='pending')  # pending, success, failed
    
    def to_dict(self):
        return {
            'id': self.id,
            'account': self.account,
            'password': self.password,
            'name': self.name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'login_status': self.login_status
        }

class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(120), nullable=False)
    level = db.Column(db.String(20), nullable=False)  # INFO, ERROR, DEBUG
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    
    def to_dict(self):
        return {
            'id': self.id,
            'account_name': self.account_name,
            'level': self.level,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'date': self.date
        }

class EmailConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    smtp_server = db.Column(db.String(120), nullable=False)
    smtp_port = db.Column(db.Integer, nullable=False)
    sender_email = db.Column(db.String(120), nullable=False)
    sender_password = db.Column(db.String(120), nullable=False)
    receiver_email = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'sender_email': self.sender_email,
            'sender_password': self.sender_password,
            'receiver_email': self.receiver_email,
            'is_active': self.is_active
        }

class SchedulerConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hour1 = db.Column(db.Integer, default=9)
    minute1 = db.Column(db.Integer, default=30)
    hour2 = db.Column(db.Integer, default=11)
    minute2 = db.Column(db.Integer, default=50)
    is_enabled = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'hour1': self.hour1,
            'minute1': self.minute1,
            'hour2': self.hour2,
            'minute2': self.minute2,
            'is_enabled': self.is_enabled
        }

# 初始化数据库
def init_database():
    with app.app_context():
        db.create_all()
        
        # 检查是否有默认账号
        if Account.query.count() == 0:
            default_account = Account(
                account='tbh2356@126.com',
                password='112233qq',
                name='tbh2356@126.com'
            )
            db.session.add(default_account)
        
        # 检查是否有默认邮箱配置
        if EmailConfig.query.count() == 0:
            default_email = EmailConfig(
                smtp_server='smtp.email.cn',
                smtp_port=465,
                sender_email='18@HH.email.cn',
                sender_password='yuHKfnKvCqmw6HNN',
                receiver_email='Steven@HH.email.cn'
            )
            db.session.add(default_email)
        
        # 检查是否有默认调度配置
        if SchedulerConfig.query.count() == 0:
            default_scheduler = SchedulerConfig()
            db.session.add(default_scheduler)
        
        db.session.commit()

# 自动登录类
class AutoLogin:
    def __init__(self, account_id):
        self.account_id = account_id
        self.account = Account.query.get(account_id)
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "Referer": "https://cms.ayybyyy.com/"
        }
        self.ocr = ddddocr.DdddOcr()
        self.max_attempts = 5
        self.first_public_key = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDNR7I+SpqIZM5w3Aw4lrUlhrs7VurKbeViYXNhOfIgP/4acsWvJy5dPb/FejzUiv2cAiz5As2DJEQYEM10LvnmpnKx9Dq+QDo7WXnT6H2szRtX/8Q56Rlzp9bJMlZy7/i0xevlDrWZMWqx2IK3ZhO9+0nPu4z4SLXaoQGIrs7JxwIDAQAB"
        
    def log_message(self, level, message):
        """记录日志到数据库"""
        log_entry = LogEntry(
            account_name=self.account.name,
            level=level,
            message=message,
            date=datetime.now().strftime('%Y-%m-%d')
        )
        db.session.add(log_entry)
        db.session.commit()
        
        # 同时记录到文件日志
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"login_{today}.log")
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - {message}\n")
    
    def get_token(self):
        """获取token"""
        url = "https://cmsapi3.qiucheng-wangluo.com/cms-api/token/generateCaptchaToken"
        try:
            response = self.session.post(url, headers=self.headers)
            if response.status_code == 200:
                result = response.json()
                if result.get("iErrCode") == 0:
                    return result.get("result")
                else:
                    self.log_message("ERROR", f"获取token失败: {result.get('sErrMsg', '未知错误')}")
            else:
                self.log_message("ERROR", f"获取token请求失败，状态码: {response.status_code}")
        except Exception as e:
            self.log_message("ERROR", f"获取token时发生异常: {str(e)}")
        return None
    
    def get_captcha(self, token):
        """获取验证码图片"""
        url = "https://cmsapi3.qiucheng-wangluo.com/cms-api/captcha"
        data = {"token": token}
        try:
            response = self.session.post(url, headers=self.headers, data=data)
            if response.status_code == 200:
                result = response.json()
                if result.get("iErrCode") == 0:
                    return result.get("result")
                else:
                    self.log_message("ERROR", f"获取验证码失败: {result.get('sErrMsg', '未知错误')}")
            else:
                self.log_message("ERROR", f"获取验证码请求失败，状态码: {response.status_code}")
        except Exception as e:
            self.log_message("ERROR", f"获取验证码时发生异常: {str(e)}")
        return None
    
    def recognize_captcha(self, captcha_base64):
        """识别验证码"""
        try:
            captcha_img = base64.b64decode(captcha_base64)
            captcha_text = self.ocr.classification(captcha_img)
            captcha_text = re.sub(r'[^a-zA-Z0-9]', '', captcha_text)
            if len(captcha_text) > 4:
                captcha_text = captcha_text[:4]
            result = captcha_text.upper()
            return result
        except Exception as e:
            self.log_message("ERROR", f"识别验证码时发生异常: {str(e)}")
            return None
    
    def load_public_key(self, key_str):
        """加载公钥"""
        try:
            if "-----BEGIN" in key_str:
                return serialization.load_pem_public_key(key_str.encode(), backend=default_backend())
            else:
                try:
                    der_data = base64.b64decode(key_str)
                    return serialization.load_der_public_key(der_data, backend=default_backend())
                except:
                    try:
                        hex_str = re.sub(r'\s+', '', key_str)
                        if len(hex_str) % 2 != 0:
                            hex_str = '0' + hex_str
                        der_data = bytes.fromhex(hex_str)
                        return serialization.load_der_public_key(der_data, backend=default_backend())
                    except:
                        return serialization.load_pem_public_key(key_str.encode(), backend=default_backend())
        except Exception as e:
            self.log_message("ERROR", f"加载公钥时发生异常: {str(e)}")
            return None
    
    def rsa_encrypt_long(self, text, public_key_str):
        """RSA加密长文本"""
        try:
            public_key = self.load_public_key(public_key_str)
            if not public_key:
                return None
            
            key_size = public_key.key_size // 8
            max_block_size = key_size - 11
            
            encrypted_blocks = []
            for i in range(0, len(text), max_block_size):
                block = text[i:i + max_block_size]
                encrypted_block = public_key.encrypt(
                    block.encode('utf-8'),
                    padding.PKCS1v15()
                )
                encrypted_blocks.append(encrypted_block)
            
            encrypted_data = b''.join(encrypted_blocks)
            return base64.b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            self.log_message("ERROR", f"RSA长文本加密时发生异常: {str(e)}")
            return None
    
    def login(self, account, password, captcha, token):
        """登录"""
        url = "https://cmsapi3.qiucheng-wangluo.com/cms-api/login"
        
        first_encrypted_password = self.rsa_encrypt_long(password, self.first_public_key)
        if not first_encrypted_password:
            self.log_message("ERROR", "第一次密码加密失败")
            return None
        
        second_encrypted_password = self.rsa_encrypt_long(first_encrypted_password, token)
        if not second_encrypted_password:
            self.log_message("ERROR", "第二次密码加密失败")
            return None
        
        encrypted_account = self.rsa_encrypt_long(account, token)
        if not encrypted_account:
            self.log_message("ERROR", "账号加密失败")
            return None
        
        data = {
            "account": encrypted_account,
            "data": second_encrypted_password,
            "safeCode": captcha,
            "token": token,
            "locale": "zh"
        }
        
        try:
            response = self.session.post(url, headers=self.headers, data=data)
            if response.status_code == 200:
                return response.json()
            else:
                self.log_message("ERROR", f"登录请求失败，状态码: {response.status_code}")
                return None
        except Exception as e:
            self.log_message("ERROR", f"登录时发生异常: {str(e)}")
            return None
    
    def get_club_list(self, token):
        """获取俱乐部列表"""
        url = "https://cmsapi3.qiucheng-wangluo.com/cms-api/club/getClubList"
        headers = {
            "accept": "application/json, text/javascript",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
            "sec-ch-ua-mobile": "?0",
            "token": token,
            "referrer": "https://cms.ayybyyy.com/"
        }
        
        try:
            response = requests.post(url, headers=headers)
            if response.status_code == 200:
                result = response.json()
                if result.get("iErrCode") == 0:
                    club_data = result.get("result")
                    if isinstance(club_data, list) and len(club_data) > 0:
                        club_info = club_data[0]
                        club_id = club_info.get("lClubID")
                        club_name = club_info.get("sClubName")
                        create_user = club_info.get("lCreateUser")
                        credit_league_id = club_info.get("iCreditLeagueId")
                        
                        self.log_message("INFO", f"俱乐部信息: lClubID={club_id}, sClubName={club_name}, lCreateUser={create_user}, iCreditLeagueId={credit_league_id}")
                        return club_info
                    elif isinstance(club_data, dict):
                        club_id = club_data.get("lClubID")
                        club_name = club_data.get("sClubName")
                        create_user = club_data.get("lCreateUser")
                        credit_league_id = club_data.get("iCreditLeagueId")
                        
                        self.log_message("INFO", f"俱乐部信息: lClubID={club_id}, sClubName={club_name}, lCreateUser={create_user}, iCreditLeagueId={credit_league_id}")
                        return club_data
                    else:
                        self.log_message("ERROR", "获取俱乐部列表成功，但返回数据格式不正确")
                else:
                    error_msg = result.get("sErrMsg", "未知错误")
                    self.log_message("ERROR", f"获取俱乐部列表失败: {error_msg}")
            else:
                self.log_message("ERROR", f"获取俱乐部列表请求失败，状态码: {response.status_code}")
        except Exception as e:
            self.log_message("ERROR", f"获取俱乐部列表时发生异常: {str(e)}")
        return None
    
    def send_log_email(self):
        """发送日志邮件"""
        try:
            email_config = EmailConfig.query.first()
            if not email_config or not email_config.is_active:
                return False
            
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join("logs", f"login_{today}.log")
            
            if not os.path.exists(log_file):
                self.log_message("WARNING", "日志文件不存在，无法发送邮件")
                return False
            
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            if not log_content.strip():
                self.log_message("INFO", "日志内容为空，不发送邮件")
                return False
            
            subject = f"自动登录日志 - {today}"
            message = MIMEText(log_content, 'plain', 'utf-8')
            message['From'] = Header(email_config.sender_email)
            message['To'] = Header(email_config.receiver_email)
            message['Subject'] = Header(subject, 'utf-8')
            
            with smtplib.SMTP_SSL(
                    email_config.smtp_server,
                    email_config.smtp_port
            ) as server:
                server.login(
                    email_config.sender_email,
                    email_config.sender_password
                )
                server.sendmail(
                    email_config.sender_email,
                    [email_config.receiver_email],
                    message.as_string()
                )
            
            self.log_message("INFO", f"日志邮件已成功发送到 {email_config.receiver_email}")
            return True
        
        except Exception as e:
            self.log_message("ERROR", f"发送邮件时发生错误: {str(e)}")
            return False
    
    def run_login(self):
        """执行登录流程"""
        self.log_message("INFO", f"开始为账号 [{self.account.name}] 执行自动登录流程...")
        
        for attempt in range(1, self.max_attempts + 1):
            self.log_message("INFO", f"尝试第 {attempt} 次登录 [{self.account.name}]...")
            
            token = self.get_token()
            if not token:
                self.log_message("ERROR", "获取token失败，等待重试...")
                time.sleep(2)
                continue
            
            self.log_message("INFO", f"获取token成功: {token[:20]}...")
            
            captcha_base64 = self.get_captcha(token)
            if not captcha_base64:
                self.log_message("ERROR", "获取验证码失败，等待重试...")
                time.sleep(2)
                continue
            
            self.log_message("INFO", "获取验证码成功")
            
            captcha_text = self.recognize_captcha(captcha_base64)
            if not captcha_text or len(captcha_text) != 4:
                self.log_message("ERROR", f"验证码识别失败或格式不正确: {captcha_text}，等待重试...")
                time.sleep(2)
                continue
            
            self.log_message("INFO", f"识别验证码结果: {captcha_text}")
            
            login_result = self.login(
                self.account.account,
                self.account.password,
                captcha_text,
                token
            )
            
            if login_result:
                if login_result.get("iErrCode") == 0:
                    self.log_message("INFO", "登录成功!")
                    self.account.login_status = 'success'
                    self.account.last_login = datetime.now()
                    db.session.commit()
                    
                    club_info = self.get_club_list(token)
                    if club_info:
                        self.log_message("INFO", "获取俱乐部列表成功")
                    else:
                        self.log_message("ERROR", "获取俱乐部列表失败")
                    
                    self.send_log_email()
                    return True
                else:
                    error_msg = login_result.get("sErrMsg", "未知错误")
                    self.log_message("ERROR", f"登录失败: {error_msg}")
                    
                    if "验证码" in error_msg:
                        self.log_message("INFO", "验证码错误，立即重试...")
                        time.sleep(1)
                        continue
            else:
                self.log_message("ERROR", "登录请求失败")
            
            if attempt < self.max_attempts:
                wait_time = 2 ** attempt
                self.log_message("INFO", f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
        
        self.log_message("ERROR", f"已达到最大尝试次数 {self.max_attempts}，登录失败")
        self.account.login_status = 'failed'
        db.session.commit()
        return False

# 定时任务调度器
scheduler = BackgroundScheduler()

def scheduled_login():
    """定时登录任务"""
    with app.app_context():
        logger.info("执行定时登录任务...")
        accounts = Account.query.filter_by(is_active=True).all()
        
        for account in accounts:
            try:
                auto_login = AutoLogin(account.id)
                auto_login.run_login()
                time.sleep(3)
            except Exception as e:
                logger.error(f"处理账号 [{account.name}] 时发生异常: {str(e)}")

# 路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    accounts = Account.query.all()
    return jsonify([account.to_dict() for account in accounts])

@app.route('/api/accounts', methods=['POST'])
def add_account():
    data = request.json
    account = Account(
        account=data['account'],
        password=data['password'],
        name=data['name']
    )
    db.session.add(account)
    db.session.commit()
    return jsonify({'success': True, 'account': account.to_dict()})

@app.route('/api/accounts/<int:account_id>', methods=['PUT'])
def update_account(account_id):
    account = Account.query.get_or_404(account_id)
    data = request.json
    
    account.account = data.get('account', account.account)
    account.password = data.get('password', account.password)
    account.name = data.get('name', account.name)
    account.is_active = data.get('is_active', account.is_active)
    
    db.session.commit()
    return jsonify({'success': True, 'account': account.to_dict()})

@app.route('/api/accounts/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    account = Account.query.get_or_404(account_id)
    db.session.delete(account)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/accounts/<int:account_id>/login', methods=['POST'])
def manual_login(account_id):
    account = Account.query.get_or_404(account_id)
    
    def login_thread():
        with app.app_context():
            auto_login = AutoLogin(account_id)
            auto_login.run_login()
    
    thread = threading.Thread(target=login_thread)
    thread.start()
    
    return jsonify({'success': True, 'message': '登录任务已启动'})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    date_filter = request.args.get('date')
    account_filter = request.args.get('account')
    level_filter = request.args.get('level')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    query = LogEntry.query
    
    if date_filter:
        query = query.filter(LogEntry.date == date_filter)
    
    if account_filter:
        query = query.filter(LogEntry.account_name == account_filter)
    
    if level_filter:
        query = query.filter(LogEntry.level == level_filter)
    
    logs = query.order_by(LogEntry.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'logs': [log.to_dict() for log in logs.items],
        'total': logs.total,
        'pages': logs.pages,
        'current_page': page
    })

@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    date_filter = request.json.get('date')
    
    if date_filter:
        LogEntry.query.filter(LogEntry.date == date_filter).delete()
    else:
        LogEntry.query.delete()
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/email_config', methods=['GET'])
def get_email_config():
    config = EmailConfig.query.first()
    return jsonify(config.to_dict() if config else {})

@app.route('/api/email_config', methods=['POST'])
def update_email_config():
    data = request.json
    config = EmailConfig.query.first()
    
    if not config:
        config = EmailConfig()
    
    config.smtp_server = data.get('smtp_server', config.smtp_server)
    config.smtp_port = data.get('smtp_port', config.smtp_port)
    config.sender_email = data.get('sender_email', config.sender_email)
    config.sender_password = data.get('sender_password', config.sender_password)
    config.receiver_email = data.get('receiver_email', config.receiver_email)
    config.is_active = data.get('is_active', config.is_active)
    
    db.session.add(config)
    db.session.commit()
    return jsonify({'success': True, 'config': config.to_dict()})

@app.route('/api/scheduler_config', methods=['GET'])
def get_scheduler_config():
    config = SchedulerConfig.query.first()
    return jsonify(config.to_dict() if config else {})

@app.route('/api/scheduler_config', methods=['POST'])
def update_scheduler_config():
    data = request.json
    config = SchedulerConfig.query.first()
    
    if not config:
        config = SchedulerConfig()
    
    config.hour1 = data.get('hour1', config.hour1)
    config.minute1 = data.get('minute1', config.minute1)
    config.hour2 = data.get('hour2', config.hour2)
    config.minute2 = data.get('minute2', config.minute2)
    config.is_enabled = data.get('is_enabled', config.is_enabled)
    
    db.session.add(config)
    db.session.commit()
    
    # 更新调度器
    update_scheduler()
    
    return jsonify({'success': True, 'config': config.to_dict()})

@app.route('/api/keep_alive', methods=['GET'])
def keep_alive():
    """防止服务器闲置的接口"""
    return jsonify({'status': 'alive', 'timestamp': datetime.now().isoformat()})

def update_scheduler():
    """更新调度器配置"""
    global scheduler
    
    # 清除现有任务
    scheduler.remove_all_jobs()
    
    config = SchedulerConfig.query.first()
    if config and config.is_enabled:
        # 添加定时任务
        scheduler.add_job(
            scheduled_login,
            trigger=CronTrigger(hour=config.hour1, minute=config.minute1),
            id='login1'
        )
        scheduler.add_job(
            scheduled_login,
            trigger=CronTrigger(hour=config.hour2, minute=config.minute2),
            id='login2'
        )
        
        logger.info(f"调度器已更新: {config.hour1}:{config.minute1}, {config.hour2}:{config.minute2}")

# 初始化函数
def init_app():
    # 初始化数据库
    init_database()
    
    # 启动调度器
    scheduler.start()
    
    # 立即执行一次登录
    logger.info("立即执行一次登录...")
    scheduled_login()

if __name__ == '__main__':
    init_app()
    app.run(host='0.0.0.0', port=10000, debug=True)
