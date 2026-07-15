"""数据仓库 数据访问层"""
import json
from app.models.db import get_connection


class DataWarehouseRepository:

    @staticmethod
    def get_all(page: int = 1, page_size: int = 20, search: str = "", source_name: str = "") -> dict:
        offset = (page - 1) * page_size
        with get_connection() as conn:
            where = "WHERE 1=1"
            params = []
            if search:
                where += " AND (title LIKE ? OR summary LIKE ?)"
                params.extend([f"%{search}%", f"%{search}%"])
            if source_name:
                where += " AND source_name = ?"
                params.append(source_name)
            total = conn.execute(f"SELECT COUNT(*) as cnt FROM data_warehouse {where}", params).fetchone()["cnt"]
            rows = conn.execute(
                f"SELECT * FROM data_warehouse {where} ORDER BY id DESC LIMIT ? OFFSET ?",
                params + [page_size, offset]
            ).fetchall()
            return {"rows": [dict(r) for r in rows], "total": total}

    @staticmethod
    def get_by_id(wid: int) -> dict | None:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM data_warehouse WHERE id=?", (wid,)).fetchone()
        return dict(row) if row else None

    @staticmethod
    def save_batch(items: list[dict]) -> int:
        count = 0
        with get_connection() as conn:
            for item in items:
                exists = conn.execute("SELECT id FROM data_warehouse WHERE url=?", (item.get("url", ""),)).fetchone()
                if exists:
                    continue
                conn.execute(
                    "INSERT INTO data_warehouse (title, url, summary, source_name, source_id, keyword) VALUES (?,?,?,?,?,?)",
                    (item.get("title", ""), item.get("url", ""), item.get("summary", ""),
                     item.get("source_name", ""), item.get("source_id", 0), item.get("keyword", ""))
                )
                count += 1
        return count

    @staticmethod
    def delete(wid: int) -> bool:
        with get_connection() as conn:
            cur = conn.execute("DELETE FROM data_warehouse WHERE id=?", (wid,))
            return cur.rowcount > 0

    @staticmethod
    def delete_batch(ids: list[int]) -> int:
        with get_connection() as conn:
            placeholders = ",".join("?" for _ in ids)
            cur = conn.execute(f"DELETE FROM data_warehouse WHERE id IN ({placeholders})", ids)
            return cur.rowcount

    @staticmethod
    def mark_deep_collected(wid: int, deep_data: dict = None):
        with get_connection() as conn:
            if deep_data:
                conn.execute(
                    "UPDATE data_warehouse SET is_deep_collected=1, deep_data=? WHERE id=?",
                    (json.dumps(deep_data, ensure_ascii=False), wid)
                )
            else:
                conn.execute("UPDATE data_warehouse SET is_deep_collected=1 WHERE id=?", (wid,))

    @staticmethod
    def get_source_names() -> list[str]:
        with get_connection() as conn:
            rows = conn.execute("SELECT DISTINCT source_name FROM data_warehouse WHERE source_name != ''").fetchall()
        return [r["source_name"] for r in rows]
