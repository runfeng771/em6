# 部署指南

本文档提供了自动登录管理系统的多种部署方式。

## 目录

- [本地部署](#本地部署)
- [Docker部署](#docker部署)
- [Render部署](#render部署)
- [其他云平台部署](#其他云平台部署)
- [测试验证](#测试验证)

## 本地部署

### 方式一：使用启动脚本（推荐）

```bash
# 1. 进入项目目录
cd flask_app

# 2. 赋予启动脚本执行权限
chmod +x start.sh

# 3. 运行启动脚本
./start.sh
```

### 方式二：手动安装

```bash
# 1. 创建虚拟环境
python3 -m venv venv

# 2. 激活虚拟环境
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动应用
python app.py
```

### 方式三：使用Gunicorn（生产环境）

```bash
# 1. 安装Gunicorn
pip install gunicorn

# 2. 启动应用
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Docker部署

### 方式一：使用Docker命令

```bash
# 1. 构建镜像
docker build -t auto-login-system .

# 2. 运行容器
docker run -d -p 5000:5000 --name auto-login auto-login-system

# 3. 查看日志
docker logs auto-login
```

### 方式二：使用Docker Compose（推荐）

```bash
# 1. 启动服务
docker-compose up -d

# 2. 查看服务状态
docker-compose ps

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

## Render部署

Render是一个免费的云平台，适合部署小型应用。

### 步骤1：准备GitHub仓库

1. 将代码推送到GitHub仓库
2. 确保仓库包含以下文件：
   - `app.py` - 主应用文件
   - `requirements.txt` - Python依赖
   - `Procfile` - Render启动命令
   - `runtime.txt` - Python版本

### 步骤2：创建Render服务

1. 登录 [Render Dashboard](https://dashboard.render.com)
2. 点击 "New +" → "Web Service"
3. 选择你的GitHub仓库
4. 配置服务：
   - **Name**: `auto-login-system`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Instance Type**: `Free` (或选择付费版本)
   - **Region**: 选择离你最近的区域

### 步骤3：环境变量（可选）

在Environment标签页添加环境变量：

```bash
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key
```

### 步骤4：部署

1. 点击 "Create Web Service"
2. 等待构建完成（通常需要2-5分钟）
3. 访问提供的URL

## 其他云平台部署

### Heroku部署

```bash
# 1. 安装Heroku CLI
# 2. 登录Heroku
heroku login

# 3. 创建应用
heroku create your-app-name

# 4. 设置构建包
heroku buildpacks:set heroku/python

# 5. 部署
git push heroku main

# 6. 打开应用
heroku open
```

### PythonAnywhere部署

1. 注册PythonAnywhere账号
2. 创建新的Web应用
3. 配置：
   - **Python版本**: 3.9
   - **Web框架**: Flask
   - **工作目录**: `/home/username/auto-login`
   - **WSGI配置文件**: `/var/www/your-username-pythonanywhere-com-wsgi.py`

4. 上传代码文件
5. 安装依赖：`pip install -r requirements.txt`
6. 重启Web应用

### VPS部署

```bash
# 1. 连接到VPS
ssh user@your-server-ip

# 2. 安装必要软件
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx

# 3. 创建应用目录
sudo mkdir -p /var/www/auto-login
sudo chown $USER:$USER /var/www/auto-login

# 4. 上传代码到 /var/www/auto-login

# 5. 创建虚拟环境
cd /var/www/auto-login
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. 创建systemd服务
sudo tee /etc/systemd/system/auto-login.service > /dev/null <<EOF
[Unit]
Description=Auto Login System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/auto-login
Environment=PATH=/var/www/auto-login/venv/bin
ExecStart=/var/www/auto-login/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
EOF

# 7. 启动服务
sudo systemctl daemon-reload
sudo systemctl enable auto-login
sudo systemctl start auto-login

# 8. 配置Nginx反向代理
sudo tee /etc/nginx/sites-available/auto-login > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 9. 启用站点
sudo ln -s /etc/nginx/sites-available/auto-login /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 测试验证

### 运行测试脚本

```bash
# 在项目目录下运行
python test.py
```

测试脚本会检查：
- 依赖包是否安装正确
- 数据库连接是否正常
- 主要路由是否工作

### 手动测试

1. **访问应用**
   ```bash
   # 本地
   curl http://localhost:5000
   
   # 或在浏览器中访问
   http://localhost:5000
   ```

2. **测试API**
   ```bash
   # 测试账号API
   curl http://localhost:5000/api/accounts
   
   # 测试保活API
   curl http://localhost:5000/api/keep_alive
   ```

3. **测试功能**
   - 添加账号
   - 手动登录
   - 查看日志
   - 配置邮件
   - 设置定时任务

## 常见问题

### 1. 端口占用

如果5000端口被占用，可以修改端口：

```python
# 在app.py中修改
app.run(debug=True, host='0.0.0.0', port=5001)
```

### 2. 权限问题

确保日志目录有写入权限：

```bash
chmod 755 logs/
```

### 3. 依赖问题

如果遇到依赖问题，尝试：

```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### 4. 数据库问题

如果数据库出现问题，删除数据库文件重新创建：

```bash
rm -f auto_login.db
python -c "from app import init_database; init_database()"
```

### 5. 邮件发送失败

检查：
- SMTP服务器配置是否正确
- 邮箱密码是否正确
- 网络连接是否正常
- 是否开启了邮箱的SMTP服务

## 性能优化

### 1. 使用Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 2. 使用Nginx反向代理

配置Nginx处理静态文件和反向代理。

### 3. 使用Redis缓存

对于大量日志，可以考虑使用Redis缓存。

### 4. 定期清理日志

设置定时任务清理旧日志：

```bash
# 添加到crontab
0 2 * * * find /path/to/logs -name "*.log" -mtime +30 -delete
```

## 安全建议

1. **修改默认密码**
   - 修改默认账号密码
   - 使用强密码

2. **配置HTTPS**
   - 使用SSL证书
   - 强制HTTPS访问

3. **限制访问**
   - 使用防火墙限制访问
   - 配置IP白名单

4. **定期更新**
   - 定期更新依赖包
   - 监控安全漏洞

## 监控和维护

### 1. 日志监控

```bash
# 查看应用日志
tail -f logs/login_$(date +%Y-%m-%d).log

# 查看系统日志
journalctl -u auto-login -f
```

### 2. 健康检查

```bash
# 检查应用状态
curl http://localhost:5000/api/keep_alive
```

### 3. 备份

```bash
# 备份数据库
cp auto_login.db backup/auto_login_$(date +%Y%m%d).db

# 备份日志
tar -czf backup/logs_$(date +%Y%m%d).tar.gz logs/
```

---

如果在部署过程中遇到问题，请参考项目的README.md文件或提交Issue。