from typing import Optional
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


class UpsertSong(BaseModel):
    id: str
    title: Optional[str] = None
    publishedTimestamp: Optional[int] = None
    durationSeconds: Optional[int] = None
    thumbnailURL: Optional[str] = None
    publishedType: int
    vocal: Optional[list[str]] = None
    illustrations: Optional[list[str]] = None
    movie: Optional[list[str]] = None
    bpm: Optional[int] = None
    mainKey: Optional[int] = None
    chordRate6451: Optional[float] = None
    chordRate4561: Optional[float] = None
    mainChord: Optional[str] = None
    pianoRate: Optional[float] = None
    modulationTimes: Optional[int] = None
    comment: Optional[str] = None

    def __eq__(self, value):
        if isinstance(value, (Song, UpsertSong)):
            return self.id == value.id
        elif isinstance(value, str):
            return self.id == value
        else:
            return NotImplemented


class CreatePlaylistRequest(BaseModel):
    title: str = Field(..., description="プレイリストのタイトル", example="MIMIさん曲まとめ")
    description: str = Field("", description="プレイリストの説明", example="「MIMIさん全曲紹介」で自動作成されました。")
    video_ids: list[str] = Field(..., description="追加する動画のIDリスト", example=["7xht3kQO_TM"])
