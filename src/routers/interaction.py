from fastapi import APIRouter, Depends, HTTPException

from src.discordbot.bot import BackendDiscordClient
from src.db.comment_database import Comment, CommentsDatabase
from src.db.user_database import UsersDatabase
from src.utils.auth import get_current_user, get_firebase_users
from src.utils.dependencies import get_comments_db, get_discord_client, get_users_db
from src.utils.user_models import UpdateUser, User
from src.utils.config import privileged_user_keywords
from src.utils.fastapi_models import PostCommentRequest, UpdateCommentRequest
from src.utils.extraction import sanitize_links


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

    await bot.default_channel.send(
        f"新しいコメントが投稿されました\n表示名: {user.displayName or 'なし'} 曲ID: {songID}\n{comment.content}"
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

    await bot.default_channel.send(
        f"コメントが更新されました\n表示名: {user.displayName or 'なし'} 曲ID: {comment.songID}\n{comment.content}"
    )
    return comment
