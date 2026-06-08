import asyncio
import time
from typing import Any
import uuid

from fastapi import APIRouter, Depends, HTTPException, WebSocket

from src.discordbot.bot import BackendDiscordClient
from src.db.comment_database import Comment, CommentsDatabase
from src.db.user_database import UsersDatabase
from src.utils.auth import get_current_user, get_firebase_users
from firebase_admin import auth as firebase_auth
from src.utils.dependencies import get_comments_db, get_discord_client, get_users_db
from src.utils.user_models import UpdateUser, User
from src.utils.config import privileged_user_keywords
from src.utils.fastapi_models import PostCommentRequest, UpdateCommentRequest
from src.utils.extraction import sanitize_links
from src.utils.logger import logger

router = APIRouter(tags=["Interaction"])


@router.get("/users/me/", response_model=User)
async def get_user(users_db: UsersDatabase = Depends(get_users_db), cred: dict = Depends(get_current_user)):
    """現在認証済みのユーザーの情報を取得します。"""
    uid: str = cred.get("uid", "")

    return users_db.get_user(uid)


@router.get("/users/me/comments/", response_model=list[Comment])
async def get_user_comments(
    comments_db: CommentsDatabase = Depends(get_comments_db),
    users_db: UsersDatabase = Depends(get_users_db),
    cred: dict = Depends(get_current_user),
):
    """現在認証済みのユーザーが投稿したコメントを取得します。"""
    uid: str = cred.get("uid", "")
    user = users_db.get_user(uid)
    return comments_db.get_comments_by_user(user.id)


@router.post("/users/me/")
async def update_user(
    user: UpdateUser, users_db: UsersDatabase = Depends(get_users_db), cred: dict = Depends(get_current_user)
):
    """現在認証済みのユーザーの情報を更新します。"""
    if not cred.get("uid", None):
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")

    if not cred.get("admin", False):
        if any(keyword in (user.displayName or "") for keyword in privileged_user_keywords):
            raise HTTPException(status_code=403, detail="Display name contains restricted keywords")

    users_db.update_user(
        firebase_uid=cred.get("uid", ""), new_display_name=user.displayName, new_use_provided_icon=user.useProvidedIcon
    )
    return users_db.get_user(cred.get("uid", ""))


@router.get("/comments/", response_model=list[Comment])
async def get_comments(
    songID: str,
    comments_db: CommentsDatabase = Depends(get_comments_db),
    users_db: UsersDatabase = Depends(get_users_db),
):
    """指定した曲に投稿されたコメントを取得します。"""
    comments = comments_db.get_comments_by_song(songID)
    firebase_users = {user.firebaseUID: user for user in get_firebase_users()}
    uids = users_db.get_user_firebase_uids()

    for comment in comments:
        if firebase_users[uids[comment.user.id]].isGuest:
            comment.content = sanitize_links(comment.content)

    return comments


@router.post("/comments/", response_model=Comment)
async def add_comment(
    songID: str,
    comment: PostCommentRequest,
    comments_db: CommentsDatabase = Depends(get_comments_db),
    users_db: UsersDatabase = Depends(get_users_db),
    bot: BackendDiscordClient = Depends(get_discord_client),
    cred: dict = Depends(get_current_user),
):
    """指定した曲にコメントを投稿します。"""
    uid: str = cred.get("uid", "")
    user = users_db.get_user(uid)

    comment = Comment(songID=songID, user=user, content=comment.content)
    comments_db.add_comment(comment)

    asyncio.create_task(
        bot.default_channel.send(
            f"新しいコメントが投稿されました\n表示名: {user.displayName or 'なし'} 曲ID: {songID}\n{comment.content}"
        )
    )
    return comment


@router.delete("/comments/{comment_id}/")
async def delete_comment(
    comment_id: str,
    comments_db: CommentsDatabase = Depends(get_comments_db),
    users_db: UsersDatabase = Depends(get_users_db),
    cred: dict = Depends(get_current_user),
):
    """指定したコメントを削除します。"""
    uid: str = cred.get("uid", "")
    user = users_db.get_user(uid)
    comment = comments_db.get_comment(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user.id != user.id and not cred.get("admin", False):
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")
    comments_db.delete_comment(comment_id)
    return {"message": "Comment deleted successfully"}


@router.post("/comments/{comment_id}/", response_model=Comment)
async def update_comment(
    comment_id: str,
    new_comment: UpdateCommentRequest,
    comments_db: CommentsDatabase = Depends(get_comments_db),
    users_db: UsersDatabase = Depends(get_users_db),
    bot: BackendDiscordClient = Depends(get_discord_client),
    cred: dict = Depends(get_current_user),
):
    """指定したコメントの内容を編集します。"""
    uid: str = cred.get("uid", "")
    user = users_db.get_user(uid)
    comment = comments_db.get_comment(comment_id)
    comment.content = new_comment.content
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user.id != user.id and not cred.get("admin", False):
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")
    comments_db.update_comment(comment_id, new_comment.content)

    asyncio.create_task(
        bot.default_channel.send(
            f"コメントが更新されました\n表示名: {user.displayName or 'なし'} 曲ID: {comment.songID}\n{comment.content}"
        )
    )
    return comment


class ConnectionManager:
    def __init__(self, users_db: UsersDatabase):
        self.users_db = users_db
        self.active_connections: list[WebSocket] = []
        self.active_user: list[tuple[bool, User] | None] = []
        self.history = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.active_user.append(None)  # ユーザーデータは後で取得するため一旦 None を追加
        await websocket.send_json({"type": "history", "messages": self.history[-20:]})  # 最新20件の履歴を送信
        logger.info("WebSocket connection established")

    async def authenticate(self, websocket: WebSocket, uid: str = "", is_admin: bool = False):
        i = self.active_connections.index(websocket)
        if self.active_user[i] is not None:
            return

        user = self.users_db.get_user(uid)
        self.active_user[i] = (is_admin, user)
        for other_websocket, ws_user in zip(self.active_connections, self.active_user):
            if ws_user is None:
                continue
            is_admin, _ = ws_user

            if not is_admin:
                continue

            await self.send_personal_message(
                {
                    "type": "info",
                    "timestamp": int(time.time()),
                    "author": user.model_dump(),
                    "content": "connected",
                },
                other_websocket,
            )

        logger.info(f"WebSocket authenticated: {user.displayName or 'No Display Name'} (Admin: {is_admin})")

    async def disconnect(self, websocket: WebSocket):
        i = self.active_connections.index(websocket)
        user, is_admin = self.active_user[i][1], self.active_user[i][0]
        for other_websocket, ws_user in zip(self.active_connections, self.active_user):
            if ws_user is None:
                continue
            is_admin, _ = ws_user

            if not is_admin:
                continue

            if other_websocket == websocket:
                continue

            await self.send_personal_message(
                {
                    "type": "info",
                    "timestamp": int(time.time()),
                    "author": user.model_dump(),
                    "content": "disconnected",
                },
                other_websocket,
            )

        self.active_connections.pop(i)
        self.active_user.pop(i)

        logger.info(f"WebSocket disconnected: {user.displayName or 'No Display Name'} (Admin: {is_admin})")

    async def send_personal_message(self, message: Any, websocket: WebSocket):
        if self.active_user[self.active_connections.index(websocket)] is None:
            logger.warning("Attempted to send message to unauthenticated WebSocket connection")
            return

        await websocket.send_json(message)

    async def broadcast(self, message: Any):
        for connection in list(self.active_connections):
            if self.active_user[self.active_connections.index(connection)] is None:
                continue

            try:
                await connection.send_json(message)
            except Exception:
                if connection in self.active_connections:
                    index = self.active_connections.index(connection)
                    self.active_connections.pop(index)
                    self.active_user.pop(index)


# `manager` をモジュール初期化時に `Depends` のまま渡すと動作しないため
# インスタンス化時は `None` にし、WebSocket ハンドラ内で実際の DB を注入します。
manager = ConnectionManager(users_db=None)


@router.websocket("/share-chat/ws")
@router.websocket("/share-chat/ws/")
async def chat_ws_endpoint(
    websocket: WebSocket,
    users_db: UsersDatabase = Depends(get_users_db),
    bot: BackendDiscordClient = Depends(get_discord_client),
):
    # 実際の UsersDatabase インスタンスを ConnectionManager に注入してから接続
    manager.users_db = users_db
    await manager.connect(websocket)

    try:
        async for data in websocket.iter_json():
            if data.get("type") not in ["post", "delete", "auth"]:
                await websocket.close(code=1003, reason="Invalid message type")
                break

            if data.get("type") == "auth":
                token = data.get("token")
                if not token:
                    logger.warning("WebSocket rejected: authentication token is missing")
                    await websocket.close(code=1008, reason="Authentication required")
                    return

                try:
                    cred = firebase_auth.verify_id_token(token)
                except Exception:
                    logger.warning("WebSocket rejected: invalid authentication token")
                    await websocket.close(code=1008, reason="Invalid authentication credentials")
                    return

                uid = cred.get("uid", "")
                is_admin = cred.get("admin", False)
                await manager.authenticate(websocket, uid=uid, is_admin=is_admin)

            elif data.get("type") == "post":
                # ensure this websocket has been authenticated
                try:
                    i = manager.active_connections.index(websocket)
                except ValueError:
                    await websocket.close(code=1001, reason="Connection error")
                    break

                if manager.active_user[i] is None:
                    logger.warning("WebSocket rejected: post attempted before authentication")
                    await websocket.close(code=1008, reason="Authentication required")
                    return

                content = data.get("content", "")
                if not content or len(content) > 140:
                    await websocket.close(code=1003, reason="Content must be between 1 and 140 characters")
                    break

                is_admin, user = manager.active_user[i]
                chatID = str(uuid.uuid4())
                chat_message = {
                    "type": "post",
                    "timestamp": int(time.time()),
                    "chatID": chatID,
                    "author": user.model_dump(),
                    "content": content,
                }

                manager.history.append(chat_message)
                await manager.broadcast(chat_message)

                asyncio.create_task(
                    bot.default_channel.send(
                        f"新しいチャットメッセージが投稿されました\n表示名: {user.displayName or 'なし'}\n{content}"
                    )
                )

                logger.info(f"New chat message posted by {user.displayName or 'No Display Name'}: {content}")

            else:
                # delete
                try:
                    i = manager.active_connections.index(websocket)
                except ValueError:
                    await websocket.close(code=1001, reason="Connection error")
                    break

                if manager.active_user[i] is None:
                    logger.warning("WebSocket rejected: delete attempted before authentication")
                    await websocket.close(code=1008, reason="Authentication required")
                    return

                is_admin, user = manager.active_user[i]

                chatID = data.get("chatID", "")
                if not chatID:
                    await websocket.close(code=1003, reason="chatID is required for delete")
                    break

                if not is_admin:
                    await websocket.close(code=1008, reason="Not authorized to perform this action")
                    break

                manager.history = [msg for msg in manager.history if msg.get("chatID") != chatID]
                await manager.broadcast(
                    {
                        "type": "delete",
                        "chatID": chatID,
                    }
                )
                logger.info(f"Chat message deleted: {chatID}")

    finally:
        if websocket in manager.active_connections:
            await manager.disconnect(websocket)
