from fastapi import APIRouter, Depends, HTTPException
from src.db.songs_database import SongsDatabase
from src.db.update_youtube_data import fetch_youtube_data
from src.utils.auth import get_current_user
from src.utils.dependencies import get_db
from src.utils.fastapi_models import UpsertLyricsVec, UpsertSong
from src.utils.songs import Song


router = APIRouter(tags=["Songs"])


@router.get("/songs/{song_id}/", response_model=Song)
async def get_song_info(song_id: str, db: SongsDatabase = Depends(get_db)):
    """指定した曲の情報を取得します。"""
    song = db.get_song_by_id(song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song


@router.get("/songs_all/", response_model=list[Song], deprecated=True)
async def get_all_songs_deprecated(db: SongsDatabase = Depends(get_db)):
    """全ての曲の情報を取得します。命名規則移行のため、/songs-all/ エンドポイントの使用を推奨します。"""
    songs = db.get_all_songs()
    return songs


@router.get("/songs-all/", response_model=list[Song])
async def get_all_songs(db: SongsDatabase = Depends(get_db)):
    """全ての曲の情報を取得します。"""
    songs = db.get_all_songs()
    return songs


@router.get("/songs_count/", deprecated=True)
async def get_songs_count_deprecated(db: SongsDatabase = Depends(get_db)):
    """データベース内の曲数を取得します。命名規則移行のため、/songs-count/ エンドポイントの使用を推奨します。"""
    count = db.get_songs_count()
    return {"count": count}


@router.get("/songs-count/")
async def get_songs_count(db: SongsDatabase = Depends(get_db)):
    """データベース内の曲数を取得します。"""
    count = db.get_songs_count()
    return {"count": count}


@router.post("/songs/{song_id}/")
async def upsert_song(
    song: UpsertSong, song_id: str, cred: dict = Depends(get_current_user), db: SongsDatabase = Depends(get_db)
):
    """曲を追加、または更新します。"""
    if not cred.get("admin", False) or cred.get("editor", False):
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")

    if any(item is None for item in (song.title, song.publishedTimestamp)):
        try:
            song = await fetch_youtube_data(db, song)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail="Failed to update YouTube data")

    if db.get_song_by_id(song_id) is not None:
        db.update_song(song, song_id)
    else:
        db.add_song(song)

    return db.get_song_by_id(song_id)


@router.post("/lyrics-vector/")
async def update_lyrics_vector(
    songs_lyrics_vec: list[UpsertLyricsVec],
    cred: dict = Depends(get_current_user),
    db: SongsDatabase = Depends(get_db),
):
    """曲の歌詞ベクトル情報を一括で更新します。"""
    if not cred.get("admin", False) or cred.get("editor", False):
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")

    success = db.update_songs_lyrics_data_batch(
        {
            song_lyrics_vec.id: (song_lyrics_vec.lyricsVector, song_lyrics_vec.lyricsOfficiallyReleased)
            for song_lyrics_vec in songs_lyrics_vec
        }
    )
    return {"success": success}
