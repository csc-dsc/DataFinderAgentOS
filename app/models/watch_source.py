"""瞭望源 数据访问层"""
import json
import urllib.parse
from app.models.db import get_connection


class WatchSourceRepository:

    @staticmethod
    def get_all() -> list[dict]:
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM watch_sources ORDER BY id ASC").fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def get_enabled() -> list[dict]:
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM watch_sources WHERE status=1 ORDER BY id ASC").fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(source_id: int) -> dict | None:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM watch_sources WHERE id=?", (source_id,)).fetchone()
        return dict(row) if row else None

    @staticmethod
    def create(name: str, description: str, base_url: str, method: str, headers: str, params_template: str) -> bool:
        try:
            with get_connection() as conn:
                conn.execute(
                    "INSERT INTO watch_sources (name, description, base_url, method, headers, params_template) VALUES (?,?,?,?,?,?)",
                    (name, description, base_url, method, headers, params_template)
                )
            return True
        except Exception:
            return False

    @staticmethod
    def update(source_id: int, name: str, description: str, base_url: str, method: str, headers: str, params_template: str) -> bool:
        try:
            with get_connection() as conn:
                conn.execute(
                    "UPDATE watch_sources SET name=?, description=?, base_url=?, method=?, headers=?, params_template=? WHERE id=?",
                    (name, description, base_url, method, headers, params_template, source_id)
                )
            return True
        except Exception:
            return False

    @staticmethod
    def delete(source_id: int) -> bool:
        with get_connection() as conn:
            cursor = conn.execute("DELETE FROM watch_sources WHERE id=?", (source_id,))
            return cursor.rowcount > 0

    @staticmethod
    def toggle_status(source_id: int) -> dict | None:
        with get_connection() as conn:
            current = conn.execute("SELECT * FROM watch_sources WHERE id=?", (source_id,)).fetchone()
            if not current:
                return None
            new_status = 0 if current["status"] == 1 else 1
            conn.execute("UPDATE watch_sources SET status=? WHERE id=?", (new_status, source_id))
            return dict(conn.execute("SELECT * FROM watch_sources WHERE id=?", (source_id,)).fetchone())

    @staticmethod
    def build_request(source_id: int, keyword: str, page: int = 0) -> dict | None:
        source = WatchSourceRepository.get_by_id(source_id)
        if not source or source["status"] != 1:
            return None
        url = source["base_url"]
        params_str = source["params_template"]
        if params_str:
            params_str = params_str.replace("{keyword}", urllib.parse.quote(keyword))
            params_str = params_str.replace("{page}", str(page))
            url = f"{url}?{params_str}"
        headers = {}
        try:
            headers = json.loads(source["headers"])
        except (json.JSONDecodeError, TypeError):
            pass
        return {"url": url, "method": source["method"], "headers": headers, "source_name": source["name"]}
