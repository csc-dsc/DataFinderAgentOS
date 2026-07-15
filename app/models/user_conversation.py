"""用户对话历史 数据访问层"""
import json
from app.models.db import get_connection


class UserConversationRepository:

    @staticmethod
    def get_by_user(user_id: int) -> list[dict]:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM user_conversations WHERE user_id=? ORDER BY updated_at DESC",
                (user_id,)
            ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(conv_id: int) -> dict | None:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM user_conversations WHERE id=?", (conv_id,)).fetchone()
        return dict(row) if row else None

    @staticmethod
    def create(user_id: int, title: str = "新对话", model_id: int = 0, employee_id: int = 0) -> int:
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO user_conversations (user_id, title, model_id, employee_id) VALUES (?,?,?,?)",
                (user_id, title, model_id, employee_id)
            )
            return cursor.lastrowid

    @staticmethod
    def update_messages(conv_id: int, messages: list[dict], title: str = None):
        with get_connection() as conn:
            if title:
                conn.execute(
                    "UPDATE user_conversations SET messages=?, title=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                    (json.dumps(messages, ensure_ascii=False), title, conv_id)
                )
            else:
                conn.execute(
                    "UPDATE user_conversations SET messages=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                    (json.dumps(messages, ensure_ascii=False), conv_id)
                )

    @staticmethod
    def delete(conv_id: int) -> bool:
        with get_connection() as conn:
            cursor = conn.execute("DELETE FROM user_conversations WHERE id=?", (conv_id,))
            return cursor.rowcount > 0

    @staticmethod
    def delete_by_user(user_id: int) -> int:
        with get_connection() as conn:
            cursor = conn.execute("DELETE FROM user_conversations WHERE user_id=?", (user_id,))
            return cursor.rowcount
