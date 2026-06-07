import uuid

from pydantic import BaseModel, Field


class UserFromDB(BaseModel):
    id: str = Field(..., default_factory=lambda: str(uuid.uuid4()))
    firebaseUID: str
    displayName: str | None = None
    useProvidedIcon: bool = False


class UserFromFirebase(BaseModel):
    firebaseUID: str
    IconURL: str | None = None
    isGuest: bool = False


class User(BaseModel):
    id: str
    displayName: str | None = None
    IconURL: str | None = None
    useProvidedIcon: bool = False


class UpdateUser(BaseModel):
    displayName: str | None = Field(None, max_length=30, min_length=1)
    useProvidedIcon: bool = False


class PostChatRequest(BaseModel):
    content: str = Field(
        ..., max_length=140, description="チャットメッセージの内容", examples=["こんにちは！", "この曲いいよね！"]
    )


class DeleteChatRequest(BaseModel):
    chatID: str = Field(..., description="削除するチャットメッセージのID", examples=["1234567890"])


ChatRequest = PostChatRequest | DeleteChatRequest


class ShareChatMessage(BaseModel):
    chatID: str = Field(..., description="チャットメッセージのID", examples=["1234567890"])
    timestamp: int = Field(..., description="チャットメッセージの投稿時刻（Unixタイムスタンプ）", examples=[1700000000])
    author: User = Field(..., description="チャットメッセージの投稿者")
    content: str = Field(
        ..., max_length=2000, description="チャットメッセージの内容", examples=["こんにちは！", "この曲いいよね！"]
    )
