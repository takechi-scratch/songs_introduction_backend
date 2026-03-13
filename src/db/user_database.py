import sqlite3
from typing import Iterable
from src.utils.user_models import User, UserFromDB
from src.utils.auth import get_firebase_user, get_firebase_users


class UsersDatabase:
    def __init__(self, db_path: str = "data/songs.db"):
        """
        SQLite3を使用したユーザーデータベース

        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """データベースとテーブルを初期化"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    firebaseUID TEXT PRIMARY KEY,
                    id TEXT NOT NULL UNIQUE,
                    displayName TEXT,
                    useProvidedIcon INTEGER NOT NULL DEFAULT 0
                );
            """
            )
            conn.commit()

    def add_user(self, user: UserFromDB):
        """ユーザーを追加"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO users (id, firebaseUID, displayName, useProvidedIcon)
                VALUES (?, ?, ?, ?)
            """,
                (user.id, user.firebaseUID, user.displayName, int(user.useProvidedIcon)),
            )
            conn.commit()

    def get_user(self, firebase_uid: str) -> User:
        """ユーザーを取得"""
        firebase_user = get_firebase_user(firebase_uid)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT id, displayName, useProvidedIcon
                FROM users
                WHERE firebaseUID = ?
            """,
                (firebase_uid,),
            )
            row = cursor.fetchone()
            if row:
                return User(
                    id=row[0],
                    displayName=row[1],
                    IconURL=firebase_user.IconURL if bool(row[2]) else None,
                    useProvidedIcon=bool(row[2]),
                )
            else:
                self.add_user(UserFromDB(firebaseUID=firebase_uid))
                return self.get_user(firebase_uid)

    def get_users_by_ids(self, user_ids: Iterable[str]) -> dict[str, User]:
        """複数のユーザーIDに紐づくユーザー情報を取得"""
        if len(user_ids) == 0:
            return {}

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                f"""
                SELECT firebaseUID, id, displayName, useProvidedIcon
                FROM users
                WHERE id IN ({','.join('?' for _ in user_ids)})
            """,
                user_ids,
            )
            rows = cursor.fetchall()

        firebase_users = {user.firebaseUID: user for user in get_firebase_users()}

        users = {}
        for row in rows:
            firebase_uid, user_id, display_name, use_provided_icon = row
            firebase_user = firebase_users.get(firebase_uid)
            users[user_id] = User(
                id=user_id,
                displayName=display_name,
                IconURL=firebase_user.IconURL if bool(use_provided_icon) else None,
                useProvidedIcon=bool(use_provided_icon),
            )

        return users

    def get_user_firebase_uids(self) -> dict[str, str]:
        """ユーザーIDとFirebase UIDの対応を取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT id, firebaseUID
                FROM users
            """
            )
            rows = cursor.fetchall()

        return {row[0]: row[1] for row in rows}

    def update_user(self, firebase_uid: str, new_display_name: str | None, new_use_provided_icon: bool):
        """ユーザー情報を更新"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE users
                SET displayName = ?, useProvidedIcon = ?
                WHERE firebaseUID = ?
            """,
                (new_display_name, int(new_use_provided_icon), firebase_uid),
            )
            conn.commit()

    def delete_user(self, firebase_uid: str):
        """ユーザーを削除"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                DELETE FROM users
                WHERE firebaseUID = ?
            """,
                (firebase_uid,),
            )
            conn.commit()
