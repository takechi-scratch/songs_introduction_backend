from pydantic import BaseModel, Field, HttpUrl

from utils.songs_class import Song

class APIInfo(BaseModel):
    website: HttpUrl = Field("https://mimi.takechi.f5.si", description="公式ウェブサイトURL")
    author: str = Field("@takechi-scratch", description="API製作者")
    help: HttpUrl = Field("https://x.com/takechi_scratch", description="お問い合わせURL")

class APIError(BaseModel):
    error: str = Field(..., description="エラーメッセージ", examples=["An error occurred"])

class SongWithScore(BaseModel):
    song: Song
    score: float
