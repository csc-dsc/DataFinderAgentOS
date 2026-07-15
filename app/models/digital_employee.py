"""数字员工 数据访问层"""
from app.models.db import get_connection


class DigitalEmployeeRepository:

    @staticmethod
    def get_all() -> list[dict]:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT e.*, m.name as model_name, m.model_name as model_code
                FROM digital_employees e
                LEFT JOIN model_engines m ON e.model_id = m.id
                ORDER BY e.id ASC
            """).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def get_enabled() -> list[dict]:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT e.*, m.name as model_name, m.model_name as model_code
                FROM digital_employees e
                LEFT JOIN model_engines m ON e.model_id = m.id
                WHERE e.status=1
                ORDER BY e.id ASC
            """).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(emp_id: int) -> dict | None:
        with get_connection() as conn:
            row = conn.execute("""
                SELECT e.*, m.name as model_name, m.model_name as model_code
                FROM digital_employees e
                LEFT JOIN model_engines m ON e.model_id = m.id
                WHERE e.id=?
            """, (emp_id,)).fetchone()
        return dict(row) if row else None

    @staticmethod
    def create(name: str, description: str, avatar: str, system_prompt: str, model_id: int) -> bool:
        try:
            with get_connection() as conn:
                conn.execute(
                    "INSERT INTO digital_employees (name, description, avatar, system_prompt, model_id) VALUES (?,?,?,?,?)",
                    (name, description, avatar, system_prompt, model_id)
                )
            return True
        except Exception:
            return False

    @staticmethod
    def update(emp_id: int, name: str, description: str, avatar: str, system_prompt: str, model_id: int) -> bool:
        try:
            with get_connection() as conn:
                conn.execute(
                    "UPDATE digital_employees SET name=?, description=?, avatar=?, system_prompt=?, model_id=? WHERE id=?",
                    (name, description, avatar, system_prompt, model_id, emp_id)
                )
            return True
        except Exception:
            return False

    @staticmethod
    def delete(emp_id: int) -> bool:
        with get_connection() as conn:
            cursor = conn.execute("DELETE FROM digital_employees WHERE id=?", (emp_id,))
            return cursor.rowcount > 0

    @staticmethod
    def toggle_status(emp_id: int) -> dict | None:
        with get_connection() as conn:
            current = conn.execute("SELECT * FROM digital_employees WHERE id=?", (emp_id,)).fetchone()
            if not current:
                return None
            new_status = 0 if current["status"] == 1 else 1
            conn.execute("UPDATE digital_employees SET status=? WHERE id=?", (new_status, emp_id))
            return dict(conn.execute("SELECT * FROM digital_employees WHERE id=?", (emp_id,)).fetchone())
