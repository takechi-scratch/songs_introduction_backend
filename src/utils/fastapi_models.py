from typing import Literal, Optional
from pydantic import BaseModel, Field, HttpUrl

from src.utils.songs import Song, SongsCustomParameters


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


# 旧検索APIで使用
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
    lyricsVector: Optional[list[float]] = None
    lyricsOfficiallyReleased: Optional[bool] = None
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


class UpsertLyricsVec(BaseModel):
    id: str = Field(..., description="曲のID")
    lyricsVector: Optional[list[float]] = Field(default=None, description="歌詞ベクトル情報")
    lyricsOfficiallyReleased: bool = Field(default=False, description="歌詞が公式から公開されているか")


SortableKey = Literal[
    "id",
    "title",
    "publishedTimestamp",
    "durationSeconds",
    "bpm",
    "mainKey",
    "chordRate6451",
    "chordRate4561",
    "pianoRate",
    "modulationTimes",
    "similarityScore",
]


class SongFilters(BaseModel):
    title: Optional[str] = Field(default=None, description="曲名（文字列詳細検索）", max_length=100)
    comment: Optional[str] = Field(default=None, description="コメント（文字列詳細検索）", max_length=100)
    vocal: Optional[str] = Field(default=None, description="ボーカル名（完全一致のみ、詳細検索）", max_length=50)
    illustrations: Optional[str] = Field(
        default=None, description="イラストレーター名（完全一致のみ、詳細検索）", max_length=50
    )
    movie: Optional[str] = Field(default=None, description="動画制作者名（完全一致のみ、詳細検索）", max_length=50)
    id: Optional[str] = Field(default=None, description="動画ID（完全一致のみ）")
    mainChord: Optional[str] = Field(default=None, description="主なコード（完全一致のみ）")
    mainKey: Optional[int] = Field(default=None, description="主なキー（完全一致のみ）")
    publishedType: Optional[int] = Field(default=None, description="公開タイプ（完全一致のみ）")
    publishedAfter: Optional[int] = Field(default=None, description="タイムスタンプ以降の曲")
    publishedBefore: Optional[int] = Field(default=None, description="タイムスタンプ以前の曲")


class SongNearestQuery(BaseModel):
    targetSongID: str = Field(..., description="基準となる曲のID")
    parameters: Optional[SongsCustomParameters] = Field(
        default=None,
        description="類似度計算に使用するパラメータ。指定しない場合はデフォルトの重みで計算されます。",
    )


class SongSearchParams(BaseModel):
    q: Optional[str] = Field(..., max_length=200, description="検索キーワード", example="初音ミク")
    filter: Optional[SongFilters] = Field(default=None, description="曲の絞り込み条件")
    nearest: Optional[SongNearestQuery] = Field(default=None, description="類似曲検索の条件")
    limit: Optional[int] = Field(None, ge=1, description="取得する曲の最大数")
    order: Optional[SortableKey] = Field(default=None, description="並び替えの基準項目")
    asc: Optional[bool] = Field(default=False, description="昇順・降順の指定")
