# 自动登录管理系统

一个基于Flask的自动登录管理系统，支持多账号管理、定时任务、日志查看等功能。

## 功能特点

- 🎯 **多账号管理**: 支持添加、编辑、删除多个账号
- ⏰ **定时任务**: 可设置定时自动登录，支持多个时间点
- 📊 **日志系统**: 完整的日志记录和查看功能，支持过滤和分页
- 🔄 **自动刷新**: 可配置的日志自动刷新功能
- 📧 **邮件通知**: 登录成功后自动发送日志邮件
- 🎨 **美观界面**: 响应式设计，友好的用户界面
- 🚀 **防止闲置**: 自动保活机制，防止服务器被关闭

## 技术栈

- **后端**: Flask, SQLAlchemy, APScheduler
- **前端**: Bootstrap 5, Font Awesome, SweetAlert2
- **OCR识别**: ddddocr
- **加密**: cryptography
- **数据库**: SQLite

## 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd flask_app
```

### 2. 安装依赖

```bash
# 使用启动脚本（推荐）
chmod +x start.sh
./start.sh

# 或手动安装
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 启动应用

```bash
python app.py
```

应用将在 `http://localhost:5000` 启动。

## 部署到Render

### 1. 准备项目

确保项目结构如下：

```
flask_app/
├── app.py
├── requirements.txt
├── start.sh
├── templates/
│   └── index.html
├── static/
│   ├── js/
│   │   └── app.js
│   └── css/
└── logs/
```

### 2. 创建Render服务

1. 登录 [Render](https://render.com)
2. 创建新的Web Service
3. 选择GitHub仓库
4. 配置服务：
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Port**: 5000

### 3. 环境变量（可选）

如果需要自定义配置，可以设置以下环境变量：

- `FLASK_ENV`: `production`
- `SECRET_KEY`: 你的密钥

## 使用说明

### 账号管理

1. **添加账号**: 点击"添加账号"按钮，填写账号信息
2. **编辑账号**: 点击账号行中的编辑按钮
3. **删除账号**: 点击账号行中的删除按钮
4. **手动登录**: 点击账号行中的登录按钮，立即执行登录

### 日志查看

1. **查看日志**: 切换到"日志查看"标签页
2. **过滤日志**: 可按日期、账号、日志级别过滤
3. **自动刷新**: 可设置5秒、10秒、20秒自动刷新
4. **清空日志**: 可清空指定日期或所有日志

### 系统设置

1. **邮件配置**: 配置SMTP服务器和邮箱信息
2. **定时任务**: 设置定时执行时间和启用状态

## 默认配置

### 默认账号
- 邮箱: `tbh2356@126.com`
- 密码: `112233qq`
- 名称: `tbh2356@126.com`

### 默认邮件配置
- SMTP服务器: `smtp.email.cn`
- SMTP端口: `465`
- 发件人: `18@HH.email.cn`
- 收件人: `Steven@HH.email.cn`

### 默认定时任务
- 第一次: `09:30`
- 第二次: `11:50`

## API接口

### 账号管理
- `GET /api/accounts` - 获取所有账号
- `POST /api/accounts` - 添加账号
- `PUT /api/accounts/<id>` - 更新账号
- `DELETE /api/accounts/<id>` - 删除账号
- `POST /api/accounts/<id>/login` - 手动登录

### 日志管理
- `GET /api/logs` - 获取日志列表
- `POST /api/logs/clear` - 清空日志

### 配置管理
- `GET /api/email_config` - 获取邮件配置
- `POST /api/email_config` - 更新邮件配置
- `GET /api/scheduler_config` - 获取定时任务配置
- `POST /api/scheduler_config` - 更新定时任务配置

### 保活接口
- `GET /api/keep_alive` - 保活请求

## 注意事项

1. **安全性**: 请妥善保管账号密码信息
2. **邮件配置**: 确保SMTP服务器配置正确
3. **定时任务**: 服务器时间可能影响定时执行
4. **日志文件**: 日志会同时保存在数据库和文件中
5. **OCR识别**: 验证码识别准确率可能影响登录成功率

## 故障排除

### 常见问题

1. **登录失败**
   - 检查账号密码是否正确
   - 查看日志中的错误信息
   - 确认网络连接正常

2. **邮件发送失败**
   - 检查SMTP配置
   - 确认邮箱密码正确
   - 检查网络连接

3. **定时任务不执行**
   - 检查定时任务是否启用
   - 确认时间设置正确
   - 查看应用日志

### 日志位置

- 应用日志: `logs/login_YYYY-MM-DD.log`
- 数据库日志: 通过Web界面查看

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License