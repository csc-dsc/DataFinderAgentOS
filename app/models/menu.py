"""
menu.py — 菜单表的仓储对象

菜单独立于功能权限，专用于 UI 导航展示。
角色通过 role_menus 关联表获得菜单可见性。
"""

from app.models.db import get_connection


class MenuRepository:
    """菜单数据访问类"""

    @staticmethod
    def get_all(page: int = 1, page_size: int = 100) -> tuple:
        with get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) as cnt FROM menus").fetchone()["cnt"]
            rows = conn.execute(
                "SELECT * FROM menus ORDER BY parent_id ASC, sort_order ASC, id ASC "
                "LIMIT ? OFFSET ?",
                (page_size, (page - 1) * page_size),
            ).fetchall()
        return rows, total

    @staticmethod
    def get_by_id(menu_id: int):
        with get_connection() as conn:
            return conn.execute(
                "SELECT * FROM menus WHERE id = ?", (menu_id,)
            ).fetchone()

    @staticmethod
    def get_by_code(code: str):
        with get_connection() as conn:
            return conn.execute(
                "SELECT * FROM menus WHERE code = ?", (code,)
            ).fetchone()

    @staticmethod
    def get_parent_options(exclude_id: int = None) -> list:
        with get_connection() as conn:
            query = "SELECT id, name FROM menus WHERE parent_id IS NULL AND is_enabled = 1"
            params = []
            if exclude_id:
                query += " AND id != ?"
                params.append(exclude_id)
            query += " ORDER BY sort_order ASC"
            return conn.execute(query, params).fetchall()

    @staticmethod
    def create(code: str, name: str, path: str = "", icon: str = "",
               sort_order: int = 0, parent_id: int = None) -> int:
        with get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO menus (code, name, path, icon, sort_order, parent_id) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (code.strip(), name.strip(), path.strip(), icon.strip(),
                 sort_order, parent_id),
            )
            conn.commit()
            return cur.lastrowid

    @staticmethod
    def update(menu_id: int, code: str = None, name: str = None, path: str = None,
               icon: str = None, sort_order: int = None, parent_id: int = None) -> bool:
        fields = {}
        if code is not None:
            fields["code"] = code.strip()
        if name is not None:
            fields["name"] = name.strip()
        if path is not None:
            fields["path"] = path.strip()
        if icon is not None:
            fields["icon"] = icon.strip()
        if sort_order is not None:
            fields["sort_order"] = sort_order
        if parent_id is not None:
            fields["parent_id"] = parent_id
        if not fields:
            return False
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [menu_id]
        with get_connection() as conn:
            conn.execute(f"UPDATE menus SET {set_clause} WHERE id = ?", values)
            conn.commit()
            return conn.total_changes > 0

    @staticmethod
    def delete(menu_id: int) -> bool:
        with get_connection() as conn:
            conn.execute("DELETE FROM role_menus WHERE menu_id = ?", (menu_id,))
            conn.execute("DELETE FROM menus WHERE parent_id = ?", (menu_id,))
            conn.execute("DELETE FROM menus WHERE id = ?", (menu_id,))
            conn.commit()
        return True

    @staticmethod
    def toggle_enabled(menu_id: int) -> int:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT is_enabled FROM menus WHERE id = ?", (menu_id,)
            ).fetchone()
            if not row:
                return -1
            new_status = 0 if row["is_enabled"] == 1 else 1
            conn.execute("UPDATE menus SET is_enabled = ? WHERE id = ?", (new_status, menu_id))
            if new_status == 0:
                conn.execute("DELETE FROM role_menus WHERE menu_id = ?", (menu_id,))
            conn.commit()
            return new_status

    @staticmethod
    def get_count() -> int:
        with get_connection() as conn:
            return conn.execute("SELECT COUNT(*) as cnt FROM menus").fetchone()["cnt"]

    @staticmethod
    def get_user_menus(username: str) -> list:
        """获取用户可见的菜单列表（根据角色-菜单关联）。"""
        with get_connection() as conn:
            user = conn.execute(
                "SELECT role_id FROM users WHERE username = ? AND is_enabled = 1",
                (username,),
            ).fetchone()
            if not user or not user["role_id"]:
                return []
            rows = conn.execute(
                """SELECT m.* FROM menus m
                   INNER JOIN role_menus rm ON m.id = rm.menu_id
                   WHERE rm.role_id = ? AND m.is_enabled = 1
                   ORDER BY m.sort_order ASC, m.id ASC""",
                (user["role_id"],),
            ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def get_user_menu_tree(username: str) -> list:
        """获取用户可见的菜单树。"""
        menus = MenuRepository.get_user_menus(username)
        menu_map = {}
        tree = []
        for m in menus:
            node = {
                "id": m["id"],
                "code": m["code"],
                "name": m["name"],
                "path": m["path"],
                "icon": m["icon"],
                "sort_order": m["sort_order"],
                "children": [],
            }
            menu_map[m["id"]] = node
        for m in menus:
            node = menu_map[m["id"]]
            if m["parent_id"] is None:
                tree.append(node)
            elif m["parent_id"] in menu_map:
                menu_map[m["parent_id"]]["children"].append(node)
        # 排序并清理空 children
        def clean(nodes):
            nodes.sort(key=lambda x: x["sort_order"])
            for n in nodes:
                if not n["children"]:
                    del n["children"]
                else:
                    clean(n["children"])
        clean(tree)
        return tree
