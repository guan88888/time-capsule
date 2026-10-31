# 时空胶囊后端API

基于FastAPI + SQLAlchemy + PyMySQL开发的后端服务。

## 环境要求

- Python 3.8+
- MySQL 5.7+

## 安装依赖

```bash
pip install -r requirements.txt
```

## 数据库配置

在 `app/database.py` 中配置数据库连接信息：

- 地址：127.0.0.1:3306
- 用户名：root
- 密码：REDACTED_SECRET
- 数据库名：my_app

**注意**：首次运行会自动创建数据库和表，确保MySQL服务已启动。

## 启动服务

```bash
python main.py
```

或者使用uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后访问：
- API文档：http://localhost:8000/docs
- 交互式API文档：http://localhost:8000/redoc

## API接口

### 认证相关 (`/api/auth`)

1. **注册** - `POST /api/auth/register`
   - 请求体：`{nickname, account, password}`
   - 返回：`{token, user}`

2. **登录** - `POST /api/auth/login`
   - 请求体：`{account, password}`
   - 返回：`{token, user}`

3. **忘记密码** - `POST /api/auth/forgot-password`
   - 请求体：`{account}`
   - 返回：`{message, success}`

4. **重置密码** - `POST /api/auth/reset-password`
   - 请求体：`{account, new_password, code?}`
   - 返回：`{message, success}`

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── database.py      # 数据库配置
│   ├── models.py        # 数据模型
│   ├── schemas.py       # Pydantic模型
│   ├── utils.py         # 工具函数
│   └── routers/
│       ├── __init__.py
│       └── auth.py      # 认证路由
├── main.py              # 应用入口
├── requirements.txt     # 依赖列表
└── README.md           # 说明文档
```

## 注意事项

1. 生产环境需要：
   - 修改 `app/utils.py` 中的 `SECRET_KEY`
   - 配置环境变量
   - 设置CORS允许的具体域名
   - 实现完整的邮件/短信验证码功能

2. 密码使用bcrypt加密存储

3. JWT token有效期30天

