from typing import Literal, Optional
from pydantic import BaseModel, Field, HttpUrl

from src.utils.songs import Song, SongsCustomParameters


class APIInfo(BaseModel):
    website: HttpUrl = Field("https://mimi.takechi.cloud", description="公式ウェブサイトURL")
    author: str = Field("@takechi-scratch", description="API製作者")
    help: HttpUrl = Field("https://x.com/takechi_scratch", description="お問い合わせURL")


class APIError(BaseModel):
    error: str = Field(..., description="エラーメッセージ", examples=["An error occurred"])


class SongWithScore(BaseModel):
    id: str
    song: Song
    score: Optional[float] = None


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
    title: Optional[str] = Field(
        default=None,
        description="曲名（コマンド対応）",
        max_length=100,
        examples=["ハナタバ", "ルルージュ | ゆめまぼろし"],
    )
    comment: Optional[str] = Field(
        default=None,
        description="コメント（コマンド対応）",
        max_length=100,
        examples=["ノリが良い", "良き", "疾走感 6251"],
    )
    vocal: Optional[str] = Field(
        default=None,
        description="ボーカル名（完全一致のみ、コマンド対応）",
        max_length=50,
        examples=["初音ミク 可不", "にんじん | saewool"],
    )
    illustrations: Optional[str] = Field(
        default=None,
        description="イラストレーター名（完全一致のみ、コマンド対応）",
        max_length=50,
        examples=["まころん", "みふる"],
    )
    movie: Optional[str] = Field(
        default=None,
        description="動画制作者名（完全一致のみ、コマンド対応）",
        max_length=50,
        examples=["瀬戸わらび | よろ", '"熊谷 芙美子"'],
    )
    id: Optional[str] = Field(default=None, description="動画ID（完全一致のみ）", examples=["7xht3kQO_TM"])
    mainChord: Optional[str] = Field(
        default=None, description="主なコード（完全一致のみ）", examples=["6451", "61451", "4561"]
    )
    mainKey: Optional[int] = Field(default=None, description="主なキー（完全一致のみ）", examples=[60, 63, -67])
    publishedType: Optional[int] = Field(default=None, description="公開タイプ（完全一致のみ）", examples=[-1, 0, 1])
    publishedAfter: Optional[int] = Field(default=None, description="タイムスタンプ以降の曲", examples=[1609459200])
    publishedBefore: Optional[int] = Field(default=None, description="タイムスタンプ以前の曲", examples=[1771081200])


class SongNearestQuery(BaseModel):
    targetSongID: str = Field(..., description="基準となる曲のID", examples=["7xht3kQO_TM"])
    parameters: Optional[SongsCustomParameters] = Field(
        default=None,
        description="類似度計算に使用するパラメータ。指定しない場合はデフォルトの重みで計算されます。",
    )


class SongSearchParams(BaseModel):
    q: Optional[str] = Field(
        default=None, max_length=200, description="検索キーワード", examples=["初音ミク", "ハナタバ", "良き"]
    )
    filter: Optional[SongFilters] = Field(default=None, description="曲の絞り込み条件")
    nearest: Optional[SongNearestQuery] = Field(default=None, description="類似曲検索の条件")
    limit: Optional[int] = Field(default=None, ge=1, description="取得する曲の最大数", examples=10)
    order: Optional[SortableKey] = Field(
        default=None,
        description="並び替えの基準項目（nearestを指定した場合はsimilarityScoreのみ指定可能）",
        examples=["publishedTimestamp", "similarityScore"],
    )
    asc: Optional[bool] = Field(default=False, description="昇順・降順の指定", examples=[False, True])
