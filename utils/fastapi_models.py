from pydantic import BaseModel, Field, HttpUrl

from utils.songs_class import Song, SongVideoData, SongsCustomParameters


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
    title: str = ""
    publishedTimestamp: int = 0
    durationSeconds: int = 0
    thumbnailURL: str = ""
    publishedType: int
    vocal: str
    illustrations: str
    movie: str
    bpm: int
    mainKey: int
    chordRate6451: float
    chordRate4561: float
    mainChord: str
    pianoRate: float
    modulationTimes: int
    comment: str

    def __eq__(self, value):
        if isinstance(value, Song):
            return self.id == value.id
        elif isinstance(value, str):
            return self.id == value
        else:
            return NotImplemented
