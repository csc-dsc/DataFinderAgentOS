"""模型引擎 数据访问层"""
from app.models.db import get_connection


class ModelEngineRepository:

    @staticmethod
    def get_all() -> list[dict]:
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM model_engines ORDER BY id ASC").fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def get_enabled() -> list[dict]:
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM model_engines WHERE status=1 ORDER BY id ASC").fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def get_default() -> dict | None:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM model_engines WHERE is_default=1 AND status=1 LIMIT 1").fetchone()
        return dict(row) if row else None

    @staticmethod
    def get_by_id(model_id: int) -> dict | None:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM model_engines WHERE id=?", (model_id,)).fetchone()
        return dict(row) if row else None

    @staticmethod
    def create(name: str, model_name: str, api_key: str, api_url: str, is_default: int = 0) -> bool:
        try:
            with get_connection() as conn:
                if is_default:
                    conn.execute("UPDATE model_engines SET is_default=0")
                conn.execute(
                    "INSERT INTO model_engines (name, model_name, api_key, api_url, is_default) VALUES (?,?,?,?,?)",
                    (name, model_name, api_key, api_url, is_default)
                )
            return True
        except Exception:
            return False

    @staticmethod
    def update(model_id: int, name: str, model_name: str, api_key: str, api_url: str, is_default: int) -> bool:
        try:
            with get_connection() as conn:
                if is_default:
                    conn.execute("UPDATE model_engines SET is_default=0 WHERE id!=?", (model_id,))
                conn.execute(
                    "UPDATE model_engines SET name=?, model_name=?, api_key=?, api_url=?, is_default=? WHERE id=?",
                    (name, model_name, api_key, api_url, is_default, model_id)
                )
            return True
        except Exception:
            return False

    @staticmethod
    def delete(model_id: int) -> bool:
        with get_connection() as conn:
            cursor = conn.execute("DELETE FROM model_engines WHERE id=?", (model_id,))
            return cursor.rowcount > 0

    @staticmethod
    def toggle_status(model_id: int) -> dict | None:
        with get_connection() as conn:
            current = conn.execute("SELECT * FROM model_engines WHERE id=?", (model_id,)).fetchone()
            if not current:
                return None
            new_status = 0 if current["status"] == 1 else 1
            conn.execute("UPDATE model_engines SET status=? WHERE id=?", (new_status, model_id))
            return dict(conn.execute("SELECT * FROM model_engines WHERE id=?", (model_id,)).fetchone())

    @staticmethod
    def set_default(model_id: int) -> bool:
        try:
            with get_connection() as conn:
                conn.execute("UPDATE model_engines SET is_default=0")
                conn.execute("UPDATE model_engines SET is_default=1 WHERE id=?", (model_id,))
            return True
        except Exception:
            return False
