"""
function.py — 功能权限表的仓储对象

采用 Repository 模式，提供功能权限码的 CRUD 操作。
功能权限码（code）如 "user:view", "role:edit" 用于后端权限校验。
"""

from app.models.db import get_connection


class FunctionRepository:
    """功能权限数据访问类"""

    @staticmethod
    def get_all(page: int = 1, page_size: int = 20) -> tuple:
        """分页查询所有功能，返回 (rows, total)。"""
        with get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) as cnt FROM functions").fetchone()["cnt"]
            rows = conn.execute(
                "SELECT * FROM functions ORDER BY sort_order ASC, id ASC "
                "LIMIT ? OFFSET ?",
                (page_size, (page - 1) * page_size),
            ).fetchall()
        return rows, total

    @staticmethod
    def get_by_id(func_id: int):
        with get_connection() as conn:
            return conn.execute(
                "SELECT * FROM functions WHERE id = ?", (func_id,)
            ).fetchone()

    @staticmethod
    def create(code: str, name: str, module: str = "", icon: str = "",
               route_path: str = "", parent_id: int = None, sort_order: int = 0) -> int:
        with get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO functions (code, name, module, icon, route_path, parent_id, sort_order) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (code.strip(), name.strip(), module.strip(), icon.strip(),
                 route_path.strip(), parent_id, sort_order),
            )
            conn.commit()
            return cur.lastrowid

    @staticmethod
    def update(func_id: int, code: str = None, name: str = None, module: str = None,
               icon: str = None, route_path: str = None, parent_id: int = None,
               sort_order: int = None) -> bool:
        fields = {}
        if code is not None:
            fields["code"] = code.strip()
        if name is not None:
            fields["name"] = name.strip()
        if module is not None:
            fields["module"] = module.strip()
        if icon is not None:
            fields["icon"] = icon.strip()
        if route_path is not None:
            fields["route_path"] = route_path.strip()
        if parent_id is not None:
            fields["parent_id"] = parent_id
        if sort_order is not None:
            fields["sort_order"] = sort_order
        if not fields:
            return False
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [func_id]
        with get_connection() as conn:
            conn.execute(f"UPDATE functions SET {set_clause} WHERE id = ?", values)
            conn.commit()
            return conn.total_changes > 0

    @staticmethod
    def delete(func_id: int) -> bool:
        with get_connection() as conn:
            conn.execute("DELETE FROM role_functions WHERE function_id = ?", (func_id,))
            conn.execute("DELETE FROM functions WHERE id = ?", (func_id,))
            conn.commit()
        return True

    @staticmethod
    def toggle_enabled(func_id: int) -> int:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT is_enabled FROM functions WHERE id = ?", (func_id,)
            ).fetchone()
            if not row:
                return -1
            new_status = 0 if row["is_enabled"] == 1 else 1
            conn.execute(
                "UPDATE functions SET is_enabled = ? WHERE id = ?", (new_status, func_id)
            )
            if new_status == 0:
                conn.execute("DELETE FROM role_functions WHERE function_id = ?", (func_id,))
            conn.commit()
            return new_status

    @staticmethod
    def get_count() -> int:
        with get_connection() as conn:
            return conn.execute("SELECT COUNT(*) as cnt FROM functions").fetchone()["cnt"]

    @staticmethod
    def get_enabled() -> list:
        with get_connection() as conn:
            return conn.execute(
                "SELECT * FROM functions WHERE is_enabled = 1 ORDER BY module ASC, sort_order ASC"
            ).fetchall()

    @staticmethod
    def get_by_code(code: str):
        with get_connection() as conn:
            return conn.execute(
                "SELECT * FROM functions WHERE code = ?", (code,)
            ).fetchone()

    @staticmethod
    def get_user_function_codes(username: str) -> set:
        """获取用户拥有的所有功能权限码集合。"""
        with get_connection() as conn:
            user = conn.execute(
                "SELECT role_id FROM users WHERE username = ? AND is_enabled = 1",
                (username,),
            ).fetchone()
            if not user or not user["role_id"]:
                return set()
            rows = conn.execute(
                """SELECT f.code FROM functions f
                   INNER JOIN role_functions rf ON f.id = rf.function_id
                   WHERE rf.role_id = ? AND f.is_enabled = 1""",
                (user["role_id"],),
            ).fetchall()
        return {r["code"] for r in rows}
