"""
role.py — roles 表的仓储对象

采用 Repository 模式，提供角色的 CRUD 及双体系权限管理：
- 角色→功能码（role_functions）：后端权限校验
- 角色→菜单（role_menus）：前端 UI 导航
"""

import sqlite3
from app.models.db import get_connection


class RoleRepository:
    """角色数据访问类"""

    @staticmethod
    def get_all(page: int = 1, page_size: int = 20) -> tuple:
        with get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) as cnt FROM roles").fetchone()["cnt"]
            rows = conn.execute(
                "SELECT * FROM roles ORDER BY is_system DESC, id ASC "
                "LIMIT ? OFFSET ?",
                (page_size, (page - 1) * page_size),
            ).fetchall()
        return rows, total

    @staticmethod
    def get_by_id(role_id: int):
        with get_connection() as conn:
            return conn.execute(
                "SELECT * FROM roles WHERE id = ?", (role_id,)
            ).fetchone()

    @staticmethod
    def get_by_name(name: str):
        with get_connection() as conn:
            return conn.execute(
                "SELECT * FROM roles WHERE name = ?", (name,)
            ).fetchone()

    @staticmethod
    def create(name: str, description: str = "") -> bool:
        try:
            with get_connection() as conn:
                conn.execute(
                    "INSERT INTO roles (name, description) VALUES (?, ?)",
                    (name.strip(), description.strip()),
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    @staticmethod
    def update(role_id: int, name: str, description: str = "") -> bool:
        try:
            with get_connection() as conn:
                conn.execute(
                    "UPDATE roles SET name = ?, description = ? WHERE id = ?",
                    (name.strip(), description.strip(), role_id),
                )
                conn.commit()
            return conn.total_changes > 0
        except sqlite3.IntegrityError:
            return False

    @staticmethod
    def delete(role_id: int) -> bool:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT is_system FROM roles WHERE id = ?", (role_id,)
            ).fetchone()
            if not row or row["is_system"] == 1:
                return False
            conn.execute("UPDATE users SET role_id = NULL WHERE role_id = ?", (role_id,))
            conn.execute("DELETE FROM roles WHERE id = ?", (role_id,))
            conn.commit()
        return True

    @staticmethod
    def get_count() -> int:
        with get_connection() as conn:
            return conn.execute("SELECT COUNT(*) as cnt FROM roles").fetchone()["cnt"]

    # ── 功能权限关联 ──────────────────────────────────────────────

    @staticmethod
    def get_function_ids(role_id: int) -> list:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT function_id FROM role_functions WHERE role_id = ?",
                (role_id,),
            ).fetchall()
        return [r["function_id"] for r in rows]

    @staticmethod
    def set_functions(role_id: int, function_ids: list[int]):
        with get_connection() as conn:
            conn.execute("DELETE FROM role_functions WHERE role_id = ?", (role_id,))
            conn.executemany(
                "INSERT INTO role_functions (role_id, function_id) VALUES (?, ?)",
                [(role_id, fid) for fid in function_ids],
            )
            conn.commit()

    # ── 菜单关联 ──────────────────────────────────────────────────

    @staticmethod
    def get_menu_ids(role_id: int) -> list:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT menu_id FROM role_menus WHERE role_id = ?",
                (role_id,),
            ).fetchall()
        return [r["menu_id"] for r in rows]

    @staticmethod
    def set_menus(role_id: int, menu_ids: list[int]):
        with get_connection() as conn:
            conn.execute("DELETE FROM role_menus WHERE role_id = ?", (role_id,))
            conn.executemany(
                "INSERT INTO role_menus (role_id, menu_id) VALUES (?, ?)",
                [(role_id, mid) for mid in menu_ids],
            )
            conn.commit()
