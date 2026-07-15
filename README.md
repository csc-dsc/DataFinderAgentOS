# 智能耗望与智能问数系统 (DataFinderAgentOS) v0.3

基于 Tornado 异步 Web 框架构建的智能数据查询与分析平台，支持 AI 对话、数据采集、知识管理等功能。

## 版本更新

- **v0.3**: 全面升级为「智能瞭望与智能问数系统」，新增 AI 智能对话、数据瞭望采集、数据仓库管理、数字员工等功能模块
- v0.2: 增强了用户管理功能，优化了数据库结构，新增角色权限管理
- v0.1: 初始版本，基础登录和管理功能

## 技术栈

- **语言**: Python 3.11+
- **Web 框架**: Tornado 6.x
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
│   │   ├── home.py          # 前台主页处理器
│   │   ├── admin_home.py    # 后台管理主页
│   │   ├── admin_user.py    # 用户管理
│   │   ├── admin_role.py    # 角色管理
│   │   ├── admin_function.py # 功能权限管理
│   │   ├── admin_menu.py    # 菜单管理
│   │   └── fingerprint.py   # 浏览器指纹采集
│   ├── models/              # 数据模型层
│   │   ├── db.py            # 数据库连接与初始化
│   │   ├── user.py          # 用户仓储
│   │   ├── role.py          # 角色仓储
│   │   ├── function.py      # 功能权限仓储
│   │   ├── menu.py          # 菜单仓储
│   │   └── fingerprint.py   # 指纹仓储
│   ├── templates/           # Tornado 模板
│   │   ├── base.html        # 基础模板
│   │   ├── login.html       # 登录页（暗色主题 + 粒子动画）
│   │   └── admin/           # 后台模板
│   │       ├── base_layout.html  # 后台布局
│   │       ├── index.html        # 管理后台主页
│   │       ├── user_list.html    # 用户列表
│   │       ├── role_list.html    # 角色列表
│   │       └── ...               # 其他管理页面
│   └── static/              # 静态资源
│       ├── css/base.css     # 基础样式
│       └── js/base.js       # 基础脚本
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
- 默认管理员账号: admin / admin888

## 功能特性

### 前台功能
- ✅ AI 智能对话（支持多模型切换）
- ✅ 数据瞭望采集（多数据源聚合）
- ✅ 数据仓库管理（采集数据存储与查询）
- ✅ 数字员工系统（@召唤专属助手）

### 后台管理
- ✅ 用户管理（CRUD + 启用/禁用）
- ✅ 角色管理（RBAC 权限控制）
- ✅ 功能权限管理（细粒度权限码）
- ✅ 菜单管理（动态导航菜单）
- ✅ 浏览器指纹采集（用户行为分析）

### 安全特性
- ✅ PBKDF2-SHA256 密码哈希 + 随机盐
- ✅ 基于 Secure Cookie 的会话管理
- ✅ XSRF 跨站请求伪造防护
- ✅ SQL 参数化查询防注入
- ✅ 已登录用户自动跳转后台

## 页面预览

### 登录页
暗色主题 + 动态粒子动画 + 玻璃拟态卡片

### 管理后台
渐变色顶栏 + 暗色侧边栏 + 统计卡片 + 现代化表格

## 安全说明

本项目为原型框架版本，生产环境部署前需：
1. 更换 `cookie_secret` 为强随机字符串，并通过环境变量注入
2. 关闭 `debug=True`
3. 配置 HTTPS + 反向代理（Nginx/Caddy）
4. 添加登录失败次数限制（防暴力破解）
5. 定期备份 `database/finderos.db`

## 团队信息

- **团队**: 明远湖大豆包
- **成员**: 陈书成
- **GitHub**: https://github.com/csc-dsc/DataFinderAgentOS
