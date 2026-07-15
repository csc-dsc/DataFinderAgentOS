"""
fingerprint.py — 浏览器指纹数据访问
"""

from app.models.db import get_connection


class FingerprintRepository:

    @staticmethod
    def save(data: dict) -> int:
        with get_connection() as conn:
            cur = conn.execute(
                """INSERT INTO fingerprints
                   (fingerprint, user_agent, platform, screen_w, screen_h,
                    color_depth, timezone, language, cpu_cores, memory_gb,
                    touch_points, canvas_hash, webgl_hash, fonts_hash,
                    pixel_ratio, url, referrer, user_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    data.get("fingerprint", ""),
                    data.get("userAgent", ""),
                    data.get("platform", ""),
                    data.get("screenW", 0),
                    data.get("screenH", 0),
                    data.get("colorDepth", 0),
                    data.get("timezone", ""),
                    data.get("language", ""),
                    str(data.get("hardwareConcurrency", "")),
                    str(data.get("deviceMemory", "")),
                    data.get("maxTouchPoints", 0),
                    data.get("canvas", ""),
                    data.get("webgl", ""),
                    data.get("fonts", ""),
                    data.get("pixelRatio", 1.0),
                    data.get("url", ""),
                    data.get("referrer", ""),
                    data.get("userId", ""),
                ),
            )
            conn.commit()
            return cur.lastrowid

    @staticmethod
    def get_all(page: int = 1, page_size: int = 50):
        with get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) as cnt FROM fingerprints").fetchone()["cnt"]
            rows = conn.execute(
                "SELECT * FROM fingerprints ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (page_size, (page - 1) * page_size),
            ).fetchall()
        return rows, total

    @staticmethod
    def get_by_fingerprint(fp: str):
        with get_connection() as conn:
            return conn.execute(
                "SELECT * FROM fingerprints WHERE fingerprint = ? ORDER BY created_at DESC",
                (fp,),
            ).fetchall()
