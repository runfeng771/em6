# 项目结构

```
flask_app/
├── app.py                    # 主应用文件
├── requirements.txt          # Python依赖包
├── Procfile                 # Render部署配置
├── runtime.txt              # Python版本
├── start.sh                 # 启动脚本
├── test.py                  # 测试脚本
├── Dockerfile               # Docker配置
├── docker-compose.yml       # Docker Compose配置
├── README.md               # 项目说明
├── DEPLOYMENT.md           # 部署指南
├── .gitignore              # Git忽略文件
│
├── templates/
│   └── index.html          # 主页面模板
│
├── static/
│   ├── css/
│   │   └── custom.css      # 自定义样式
│   └── js/
│       └── app.js          # 前端JavaScript
│
└── logs/                   # 日志目录（自动创建）
```

## 文件说明

### 核心文件

- **app.py**: Flask应用主文件，包含所有路由和业务逻辑
- **requirements.txt**: Python依赖包列表
- **templates/index.html**: 主页面HTML模板
- **static/js/app.js**: 前端JavaScript逻辑

### 部署文件

- **Procfile**: Render平台部署配置
- **runtime.txt**: Python版本指定
- **Dockerfile**: Docker容器配置
- **docker-compose.yml**: Docker Compose配置
- **start.sh**: 本地启动脚本

### 文档文件

- **README.md**: 项目说明文档
- **DEPLOYMENT.md**: 详细部署指南
- **test.py**: 测试脚本

### 配置文件

- **.gitignore**: Git版本控制忽略文件
- **static/css/custom.css**: 自定义CSS样式

## 功能模块

### 1. 账号管理
- 添加、编辑、删除账号
- 账号状态管理
- 手动登录功能

### 2. 日志系统
- 日志记录和查看
- 日志过滤（日期、账号、级别）
- 自动刷新功能
- 日志清空功能

### 3. 定时任务
- 定时登录配置
- 多时间点设置
- 任务状态管理

### 4. 邮件通知
- SMTP配置
- 登录成功邮件通知
- 日志邮件发送

### 5. 系统功能
- 保活机制（防止服务器闲置）
- 响应式界面
- 深色模式支持

## 技术栈

### 后端
- **Flask**: Web框架
- **SQLAlchemy**: ORM数据库操作
- **APScheduler**: 定时任务调度
- **ddddocr**: 验证码识别
- **cryptography**: RSA加密
- **requests**: HTTP请求

### 前端
- **Bootstrap 5**: UI框架
- **Font Awesome**: 图标库
- **SweetAlert2**: 弹窗组件
- **原生JavaScript**: 交互逻辑

### 数据库
- **SQLite**: 轻量级数据库

## 部署方式

### 1. 本地部署
```bash
cd flask_app
chmod +x start.sh
./start.sh
```

### 2. Docker部署
```bash
docker-compose up -d
```

### 3. Render部署
1. 推送到GitHub
2. 在Render创建Web Service
3. 配置自动部署

### 4. 其他平台
- Heroku
- PythonAnywhere
- VPS

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

## 环境要求

- Python 3.9+
- pip包管理器
- 可选：Docker和Docker Compose

## 开发说明

### 添加新功能
1. 修改app.py添加路由
2. 更新前端HTML和JavaScript
3. 测试功能正常

### 修改样式
1. 编辑templates/index.html中的CSS
2. 或修改static/css/custom.css

### 数据库迁移
- 使用Flask-Migrate进行数据库版本管理

## 故障排除

### 常见问题
1. **端口占用**: 修改app.py中的端口
2. **权限问题**: 确保logs目录有写入权限
3. **依赖问题**: 重新安装requirements.txt
4. **数据库问题**: 删除db文件重新初始化

### 日志位置
- 应用日志: `logs/login_YYYY-MM-DD.log`
- 系统日志: 通过系统日志工具查看

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 许可证

MIT License