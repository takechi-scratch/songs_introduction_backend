from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from src.db.songs_database import SongsDatabase
from src.utils.dependencies import get_db
from src.utils.fastapi_models import SongSampleParams, SongSearchParams, SongWithScore
from src.utils.songs import Song, SongsMatchScore
from src.utils.extraction import including_video_id

import random

router = APIRouter(tags=["Search"])


@router.get("/search/", response_model=list[Song])
async def search(
    q: Optional[str] = Query(None, description="検索キーワード", example="初音ミク"),
    db: SongsDatabase = Depends(get_db),
):
    """キーワードがタイトル・クリエイター・歌詞などに含まれる曲を検索します。"""

    songs = []
    video_id = await including_video_id(q)
    if q is not None and video_id is not None:
        songs = db.search_songs(id=video_id)

    if len(songs) == 0:
        songs = db.search_songs(q=q)
    return songs


@router.get("/nearest-search/", response_model=list[SongWithScore])
async def get_nearest_songs(target_song_id: str, limit: int = Query(10, ge=1), db: SongsDatabase = Depends(get_db)):
    """指定した条件に基づいて、最も近い曲を検索します。"""
    try:
        songs_queue = db.find_nearest_song(target_song_id, limit=limit)
    except ValueError:
        raise HTTPException(status_code=404, detail="Target song not found")

    if not songs_queue:
        raise HTTPException(status_code=404, detail="No similar songs found")
    return [
        SongWithScore(
            id=song_in_queue.song.id,
            song=song_in_queue.song,
            score=float(song_in_queue.score),
        )
        for song_in_queue in songs_queue
    ]


@router.post("/advanced-search/", response_model=list[SongWithScore])
async def advanced_search(params: SongSearchParams, db: SongsDatabase = Depends(get_db)):
    """詳しいフィルター条件や、任意の重みをつけた類似度を用いた高度な検索を行います。"""
    if params.nearest and params.order and params.order != "similarityScore":
        raise HTTPException(status_code=400, detail="order must be 'similarityScore' when nearest is specified")

    search_query = {}
    search_query["q"] = params.q if params.q else None

    songs = []
    video_id = await including_video_id(params.q)
    if video_id is not None:
        songs = db.search_songs(id=video_id)
        if len(songs) > 0:
            return [SongWithScore(id=song.id, song=song) for song in songs]

    if params.filter:
        search_query |= params.filter.model_dump(exclude_none=True)

    songs = db.search_songs(**search_query, order=params.order, asc=params.asc)

    if params.nearest is None:
        songs = [SongWithScore(id=song.id, song=song) for song in songs]
        return songs[: params.limit] if params.limit else songs

    print(len(songs))
    try:
        songs = db.find_nearest_song(
            target=params.nearest.targetSongID if params.nearest else None,
            songs=songs,
            limit=params.limit if params.limit else 10,
            parameters=params.nearest.parameters if params.nearest.parameters else None,
            is_reversed=params.asc,
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Target song not found")

    if not songs:
        raise HTTPException(status_code=404, detail="No similar songs found")

    return songs


@router.post("/songs-sample/", response_model=list[Song])
async def get_songs_sample(params: SongSampleParams, db: SongsDatabase = Depends(get_db)):
    """最大分散サンプリングを用いて、おすすめ曲診断用のサンプルを取得します。"""
    similarity_cache: dict[tuple[str, str], float] = {}
    INF = 10**18
    noise = 0.05

    def get_similarity(song1: Song, song2: Song) -> float:
        if song1.id == song2.id:
            return 1.0

        if song1.id > song2.id:
            song1, song2 = song2, song1
        pair = (song1.id, song2.id)
        if pair not in similarity_cache:
            similarity_cache[pair] = SongsMatchScore(song1, song2, db.std).get_score()
        return similarity_cache[pair]

    if params.filter:
        search_query = params.filter.model_dump(exclude_none=True)
    else:
        search_query = {}

    all_songs = db.search_songs(**search_query)
    all_songs = [song for song in all_songs if song.score_can_be_calculated()]
    if not params.includeInstSongs:
        all_songs = [song for song in all_songs if len(song.vocal) > 0 and song.vocal[0] != "-"]

    if len(all_songs) <= params.limit:
        return all_songs

    samples = [random.choice(all_songs)]
    while len(samples) < params.limit:
        next_song = min(
            all_songs,
            key=lambda song: (
                max(get_similarity(song, sample) for sample in samples) + noise * random.random()
                if song not in samples
                else INF
            ),
        )
        samples.append(next_song)

    return samples
