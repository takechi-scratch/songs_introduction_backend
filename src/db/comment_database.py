import sqlite3
import time
import uuid

from pydantic import BaseModel, Field

from src.db.user_database import UsersDatabase
from src.utils.user_models import User


class Comment(BaseModel):
    id: str = Field(..., default_factory=lambda: str(uuid.uuid4()))
    songID: str
    user: User
    content: str
    createdAt: int = Field(..., default_factory=lambda: int(time.time()))
    updatedAt: int = Field(..., default_factory=lambda: int(time.time()))


class CommentsDatabase:
    def __init__(self, db_path: str = "data/songs.db"):
        """
        SQLite3を使用したコメントデータベース

        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path
        self.user_db = UsersDatabase(db_path)
        self.init_database()

    def init_database(self):
        """データベースとテーブルを初期化"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS comments (
                    id TEXT PRIMARY KEY,
                    songID TEXT NOT NULL,
                    userID TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL,
                    visible INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY (songID) REFERENCES songs(id) ON DELETE CASCADE
                    FOREIGN KEY (userID) REFERENCES users(id) ON DELETE CASCADE
                );
            """
            )
            conn.execute("PRAGMA foreign_keys = ON;")  # 外部キー制約を有効化
            conn.commit()

    def add_comment(self, comment: Comment) -> None:
        """コメントを追加"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO comments (id, songID, userID, content, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (comment.id, comment.songID, comment.user.id, comment.content, comment.createdAt, comment.updatedAt),
            )
            conn.commit()

    def get_comment(self, comment_id: str):
        """コメントIDに紐づくコメントを取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT id, songID, userID, content, created_at, updated_at, visible
                FROM comments
                WHERE id = ? AND visible = 1
            """,
                (comment_id,),
            )
            raw_comment = cursor.fetchone()
            if not raw_comment:
                return None

            user = self.user_db.get_users_by_ids([raw_comment[2]]).get(raw_comment[2])

            return Comment(
                id=raw_comment[0],
                songID=raw_comment[1],
                user=user,
                content=raw_comment[3],
                createdAt=raw_comment[4],
                updatedAt=raw_comment[5],
            )

    def get_comments_by_song(self, song_id: str) -> list[Comment]:
        """曲IDに紐づくコメントを取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT id, songID, userID, content, created_at, updated_at, visible
                FROM comments
                WHERE songID = ? AND visible = 1
                ORDER BY created_at ASC
            """,
                (song_id,),
            )
            rows = cursor.fetchall()
            users = self.user_db.get_users_by_ids([row[2] for row in rows])

            return [
                Comment(
                    id=row[0],
                    songID=row[1],
                    user=users.get(row[2]),
                    content=row[3],
                    createdAt=row[4],
                    updatedAt=row[5],
                )
                for row in rows
            ]

    def update_comment(self, comment_id: str, new_content: str):
        """コメント内容を更新"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE comments
                SET content = ?, updated_at = ?
                WHERE id = ?
            """,
                (new_content, int(time.time()), comment_id),
            )
            conn.commit()

    def delete_comment(self, comment_id: str):
        """コメントを削除（visibleをFalseにする）"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE comments
                SET visible = 0, updated_at = ?
                WHERE id = ?
            """,
                (int(time.time()), comment_id),
            )
            conn.commit()
