# 智能瞭望与智能问数系统 (DataFinderAgentOS) v0.3

基于 Tornado 异步 Web 框架构建的轻量级数据查询与分析平台。

## 版本更新

- v0.3: 升级为智能瞭望与智能问数系统，新增智能分析功能
- v0.2: 增强了用户管理功能，优化了数据库结构，新增角色权限管理
- v0.1: 初始版本，基础登录和管理功能

## 技术栈

- **语言**: Python 3.11
- **Web 框架**: Tornado
- **数据库**: SQLite3
- **前端**: Layui 2.x + 原生 HTML/CSS/JS
- **安全**: 前端 SHA256 + 服务端 PBKDF2-SHA256 双重哈希 + 随机盐 + XSRF 防护 + Secure Cookie

## 项目结构

```
DataFinderAgentOS/
├── main.py                  # 程序入口
├── requirements.txt         # Python 依赖
├── app/
│   ├── controllers/         # 控制器层
│   │   ├── auth.py          # 登录/登出处理器
│   │   ├── base.py          # 公共基础 Handler（认证）
│   │   └── home.py          # 后台管理主页处理器
│   ├── models/              # 数据模型层
│   │   ├── db.py            # 数据库连接与初始化
│   │   └── user.py          # 用户仓储（Repository 模式）
│   ├── templates/           # Tornado 模板
│   │   ├── base.html        # 基础模板
│   │   ├── login.html       # 登录页
│   │   └── admin/           # 后台模板
│   │       └── index.html   # 管理后台主页
│   └── static/              # 静态资源
│       ├── css/base.css
│       └── js/base.js
├── database/                # SQLite 数据库文件目录
└── docs/
    └── constraint.md        # 开发规范文档
```

## 快速开始

### 1. 创建虚拟环境并安装依赖

```bash
python -m venv venv

# Windows
venv\Scripts\activate
pip install -r requirements.txt

# Linux/macOS
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 启动服务

```bash
# Windows
venv\Scripts\activate
python main.py

# Linux/macOS
source venv/bin/activate
python main.py
```

### 3. 访问系统

浏览器打开 http://localhost:10010/

- 首次启动会自动创建 SQLite 数据库和 users 表
- 需要通过代码创建初始管理员账号（见下方说明）

### 4. 创建管理员账号

```python
python -c "
import hashlib
from app.models.db import init_db
from app.models.user import UserRepository
init_db()
# 前端已做 SHA256，建用户时也传 SHA256 值以保持一致
pwd_hash = hashlib.sha256(b'your_password').hexdigest()
UserRepository.create_user('admin', pwd_hash)
print('管理员账号创建成功')
"
```

## 功能特性

- ✅ 用户登录/登出（PBKDF2-SHA256 密码哈希 + 随机盐）
- ✅ 基于 Secure Cookie 的会话管理
- ✅ XSRF 跨站请求伪造防护
- ✅ SQL 参数化查询防注入
- ✅ 已登录用户自动跳转后台
- ✅ 未登录访问拦截（自动重定向到登录页）
- ✅ Layui 后台管理框架
- ✅ Repository 模式数据访问层

## 安全说明

本项目为原型框架版本，生产环境部署前需：
1. 更换 `cookie_secret` 为强随机字符串，并通过环境变量注入
2. 关闭 `debug=True`
3. 配置 HTTPS + 反向代理（Nginx/Caddy）
4. 添加登录失败次数限制（防暴力破解）
5. 定期备份 `database/finderos.db`
