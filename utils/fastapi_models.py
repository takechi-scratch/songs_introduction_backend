from pydantic import BaseModel, Field, HttpUrl

from utils.songs_class import Song, SongsCustomParameters


class APIInfo(BaseModel):
    website: HttpUrl = Field("https://mimi.takechi.f5.si", description="公式ウェブサイトURL")
    author: str = Field("@takechi-scratch", description="API製作者")
    help: HttpUrl = Field("https://x.com/takechi_scratch", description="お問い合わせURL")


class APIError(BaseModel):
    error: str = Field(..., description="エラーメッセージ", examples=["An error occurred"])


class SongWithScore(BaseModel):
    id: str
    song: Song
    score: float


class AdvancedNearestSearch(BaseModel):
    target_song_id: str
    parameters: SongsCustomParameters
    limit: int = Field(10, ge=1)
    is_reversed: bool = Field(False)
