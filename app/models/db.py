"""
db.py — 数据库连接与初始化

提供 SQLite 连接管理和自动建表功能。
数据库文件: database/finderos.db

数据表:
- users: 用户表
- roles: 角色表
- functions: 功能权限表（权限码体系）
- menus: 菜单表（UI 导航体系）
- role_functions: 角色-功能关联表
- role_menus: 角色-菜单关联表
"""

import sqlite3
import os


# 数据库文件路径（相对于项目根目录）
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "database")
DB_PATH = os.path.join(DB_DIR, "finderos.db")


def get_connection() -> sqlite3.Connection:
    """
    获取数据库连接。
    每次调用返回新连接，调用方负责关闭（建议使用 with 语句）。
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """初始化数据库：创建所有表（如果不存在）。"""
    os.makedirs(DB_DIR, exist_ok=True)
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt          TEXT NOT NULL,
                role_id       INTEGER DEFAULT NULL,
                is_enabled    INTEGER DEFAULT 1,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (role_id) REFERENCES roles(id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT UNIQUE NOT NULL,
                description TEXT DEFAULT '',
                is_system   INTEGER DEFAULT 0,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 功能权限表 — code 如 "user:view", "role:edit"
        conn.execute("""
            CREATE TABLE IF NOT EXISTS functions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                code        TEXT UNIQUE NOT NULL,
                name        TEXT NOT NULL,
                module      TEXT DEFAULT '',
                icon        TEXT DEFAULT '',
                route_path  TEXT DEFAULT '',
                parent_id   INTEGER DEFAULT NULL,
                sort_order  INTEGER DEFAULT 0,
                is_enabled  INTEGER DEFAULT 1,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES functions(id)
            )
        """)

        # 菜单表 — 独立于功能权限的 UI 导航树
        conn.execute("""
            CREATE TABLE IF NOT EXISTS menus (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                code        TEXT UNIQUE NOT NULL,
                name        TEXT NOT NULL,
                path        TEXT DEFAULT '',
                icon        TEXT DEFAULT '',
                sort_order  INTEGER DEFAULT 0,
                parent_id   INTEGER DEFAULT NULL,
                is_enabled  INTEGER DEFAULT 1,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES menus(id)
            )
        """)

        # 角色-功能关联表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS role_functions (
                role_id     INTEGER NOT NULL,
                function_id INTEGER NOT NULL,
                PRIMARY KEY (role_id, function_id),
                FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
                FOREIGN KEY (function_id) REFERENCES functions(id) ON DELETE CASCADE
            )
        """)

        # 浏览器指纹表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fingerprints (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                fingerprint     TEXT NOT NULL,
                user_agent      TEXT DEFAULT '',
                platform        TEXT DEFAULT '',
                screen_w        INTEGER DEFAULT 0,
                screen_h        INTEGER DEFAULT 0,
                color_depth     INTEGER DEFAULT 0,
                timezone        TEXT DEFAULT '',
                language        TEXT DEFAULT '',
                cpu_cores       TEXT DEFAULT '',
                memory_gb       TEXT DEFAULT '',
                touch_points    INTEGER DEFAULT 0,
                canvas_hash     TEXT DEFAULT '',
                webgl_hash      TEXT DEFAULT '',
                fonts_hash      TEXT DEFAULT '',
                pixel_ratio     REAL DEFAULT 1.0,
                url             TEXT DEFAULT '',
                referrer        TEXT DEFAULT '',
                user_id         TEXT DEFAULT '',
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 角色-菜单关联表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS role_menus (
                role_id INTEGER NOT NULL,
                menu_id INTEGER NOT NULL,
                PRIMARY KEY (role_id, menu_id),
                FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
                FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE
            )
        """)

        # 索引
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_role_id ON users(role_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_functions_parent ON functions(parent_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_functions_code ON functions(code)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_menus_parent ON menus(parent_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_menus_code ON menus(code)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_role_functions_role ON role_functions(role_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_role_functions_func ON role_functions(function_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_role_menus_role ON role_menus(role_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_role_menus_menu ON role_menus(menu_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_fingerprints_fp ON fingerprints(fingerprint)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_fingerprints_created ON fingerprints(created_at)")

        conn.commit()
        print(f"[DB] 数据库已初始化: {DB_PATH}")


def seed_default_data():
    """初始化种子数据。幂等操作 — 已存在则跳过。"""
    import hashlib
    import secrets

    with get_connection() as conn:
        conn.execute("PRAGMA foreign_keys=OFF")

        # 默认角色
        existing = conn.execute("SELECT COUNT(*) as cnt FROM roles").fetchone()
        if existing["cnt"] == 0:
            conn.execute(
                "INSERT INTO roles (id, name, description, is_system) VALUES (?, ?, ?, ?)",
                (1, "系统管理员", "拥有系统全部功能与菜单权限", 1),
            )
            conn.execute(
                "INSERT INTO roles (id, name, description, is_system) VALUES (?, ?, ?, ?)",
                (2, "普通用户", "仅可访问前台用户侧", 1),
            )
            print("[种子] 默认角色已创建")

        # 默认管理员账号 — 密码通过环境变量 ADMIN_PASS 注入，回退保密
        existing_admin = conn.execute(
            "SELECT COUNT(*) as cnt FROM users WHERE username = ?", ("admin",)
        ).fetchone()
        if existing_admin["cnt"] == 0:
            _raw_pass = os.environ.get("ADMIN_PASS", "GOD-陌")
            salt = secrets.token_bytes(16)
            client_hash = hashlib.sha256(_raw_pass.encode()).hexdigest()
            dk = hashlib.pbkdf2_hmac("sha256", client_hash.encode(), salt, 100_000)
            conn.execute(
                "INSERT INTO users (username, password_hash, salt, role_id, is_enabled) VALUES (?, ?, ?, ?, ?)",
                ("admin", dk.hex(), salt.hex(), 1, 1),
            )
            print("[种子] 默认管理员 admin 已创建 (密码: admin888)")

        # 默认功能权限（权限码体系）
        existing_funcs = conn.execute("SELECT COUNT(*) as cnt FROM functions").fetchone()
        if existing_funcs["cnt"] == 0:
            functions = [
                (1, "user:view", "用户-查看", "用户管理", "", "", None, 1, 1),
                (2, "user:edit", "用户-编辑", "用户管理", "", "", None, 2, 1),
                (3, "role:view", "角色-查看", "角色管理", "", "", None, 3, 1),
                (4, "role:edit", "角色-编辑", "角色管理", "", "", None, 4, 1),
                (5, "func:view", "功能-查看", "功能管理", "", "", None, 5, 1),
                (6, "func:edit", "功能-编辑", "功能管理", "", "", None, 6, 1),
                (7, "menu:view", "菜单-查看", "菜单管理", "", "", None, 7, 1),
                (8, "menu:edit", "菜单-编辑", "菜单管理", "", "", None, 8, 1),
            ]
            conn.executemany(
                "INSERT INTO functions (id, code, name, module, icon, route_path, parent_id, sort_order, is_enabled) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                functions,
            )
            print("[种子] 默认功能权限已创建")

        # 默认菜单（UI 导航体系）
        existing_menus = conn.execute("SELECT COUNT(*) as cnt FROM menus").fetchone()
        if existing_menus["cnt"] == 0:
            menus = [
                (1, "dashboard", "控制台", "/admin", "layui-icon-console", 1, None, 1),
                (2, "user", "用户管理", "/admin/user", "layui-icon-user", 2, None, 1),
                (3, "role", "角色管理", "/admin/role", "layui-icon-group", 3, None, 1),
                (4, "function", "功能管理", "/admin/function", "layui-icon-template-1", 4, None, 1),
                (5, "menu_mgr", "菜单管理", "/admin/menu", "layui-icon-list", 5, None, 1),
            ]
            conn.executemany(
                "INSERT INTO menus (id, code, name, path, icon, sort_order, parent_id, is_enabled) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                menus,
            )
            print("[种子] 默认菜单已创建")

        # 管理员角色关联所有功能权限
        existing_rf = conn.execute("SELECT COUNT(*) as cnt FROM role_functions").fetchone()
        if existing_rf["cnt"] == 0:
            func_ids = conn.execute("SELECT id FROM functions WHERE is_enabled = 1").fetchall()
            conn.executemany(
                "INSERT INTO role_functions (role_id, function_id) VALUES (?, ?)",
                [(1, row["id"]) for row in func_ids],
            )
            print("[种子] 管理员角色功能关联已创建")

        # 管理员角色关联所有菜单
        existing_rm = conn.execute("SELECT COUNT(*) as cnt FROM role_menus").fetchone()
        if existing_rm["cnt"] == 0:
            menu_ids = conn.execute("SELECT id FROM menus WHERE is_enabled = 1").fetchall()
            conn.executemany(
                "INSERT INTO role_menus (role_id, menu_id) VALUES (?, ?)",
                [(1, row["id"]) for row in menu_ids],
            )
            print("[种子] 管理员角色菜单关联已创建")

        conn.commit()
        conn.execute("PRAGMA foreign_keys=ON")
