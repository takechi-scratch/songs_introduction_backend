import sqlite3
import heapq
from typing import Optional
import json
from logging import getLogger, StreamHandler, DEBUG

from utils.songs_class import (
    Song,
    SongVideoData,
    SongsMatchScore,
    SongInQueue,
    SongsSTD,
    SongsCustomParameters,
)


logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

# sqliteでlist型を扱う
# 参考: https://qiita.com/t4t5u0/items/2e789dfc5edd0d01b8da
sqlite3.register_adapter(list, lambda l: json.dumps(l, ensure_ascii=False))
sqlite3.register_converter("LIST", lambda s: json.loads(s))


class SongsDatabase:
    def __init__(self, db_path: str = "db/data/songs.db"):
        """
        SQLite3を使用したSongsデータベースクラス

        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path
        self.init_database()

        if self.get_songs_count() > 0:
            self.std = SongsSTD([song for song in self.get_all_songs() if song.score_can_be_calculated()])

    def init_database(self):
        """データベースとテーブルを初期化"""
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS songs (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    publishedTimestamp INTEGER NOT NULL,
                    publishedType INTEGER NOT NULL,
                    durationSeconds INTEGER,
                    thumbnailURL TEXT,
                    vocal LIST,
                    illustrations LIST,
                    movie LIST,
                    bpm INTEGER,
                    mainKey INTEGER,
                    chordRate6451 REAL,
                    chordRate4561 REAL,
                    mainChord TEXT,
                    pianoRate REAL,
                    modulationTimes INTEGER,
                    comment TEXT
                )
            """
            )
            conn.commit()

    def add_song(self, song: Song) -> bool:
        """
        楽曲を追加

        Args:
            song: 追加する楽曲データ

        Returns:
            bool: 追加に成功した場合True、既に存在する場合False
        """
        try:
            with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                conn.execute(
                    """
                    INSERT INTO songs (
                        id, title, publishedTimestamp, publishedType,
                        durationSeconds, thumbnailURL, vocal, illustrations, movie, bpm, mainKey,
                        chordRate6451, chordRate4561, mainChord, pianoRate,
                        modulationTimes, comment
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        song.id,
                        song.title,
                        song.publishedTimestamp,
                        song.publishedType,
                        song.durationSeconds,
                        song.thumbnailURL,
                        song.vocal,
                        song.illustrations,
                        song.movie,
                        song.bpm,
                        song.mainKey,
                        song.chordRate6451,
                        song.chordRate4561,
                        song.mainChord,
                        song.pianoRate,
                        song.modulationTimes,
                        song.comment,
                    ),
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError as e:
            logger.warning(f"Error adding song: {e}")
            # 同じIDの楽曲が既に存在する場合
            return False

    def get_song_by_id(self, song_id: str) -> Optional[Song]:
        """
        IDによる楽曲取得

        Args:
            song_id: 楽曲ID

        Returns:
            Song: 見つかった楽曲、見つからない場合None
        """
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM songs WHERE id = ?", (song_id,))
            row = cursor.fetchone()

            if row:
                return Song(**row)
            return None

    def get_all_songs(self) -> list[Song]:
        """
        全楽曲を取得

        Returns:
            list[Song]: 全楽曲のリスト
        """
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM songs ORDER BY publishedTimestamp DESC")
            rows = cursor.fetchall()

            return [Song(**row) for row in rows]

    def update_song(self, song: Song, song_id: Optional[str] = None) -> bool:
        """
        楽曲を更新

        Args:
            song: 更新する楽曲データ

        Returns:
            bool: 更新に成功した場合True、楽曲が存在しない場合False
        """
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.execute(
                """
                UPDATE songs SET
                    id = ?, title = ?, publishedTimestamp = ?, publishedType = ?,
                    durationSeconds = ?, thumbnailURL = ?, vocal = ?, illustrations = ?, movie = ?,
                    bpm = ?, mainKey = ?, chordRate6451 = ?, chordRate4561 = ?,
                    mainChord = ?, pianoRate = ?, modulationTimes = ?, comment = ?
                WHERE id = ?
            """,
                (
                    # song_idは変更前、 song.idは変更後
                    song.id,
                    song.title if song.title is not None else "",
                    song.publishedTimestamp if song.publishedTimestamp is not None else 0,
                    song.publishedType,
                    song.durationSeconds if song.durationSeconds is not None else 0,
                    song.thumbnailURL if song.thumbnailURL is not None else "",
                    song.vocal,
                    song.illustrations,
                    song.movie,
                    song.bpm,
                    song.mainKey,
                    song.chordRate6451,
                    song.chordRate4561,
                    song.mainChord,
                    song.pianoRate,
                    song.modulationTimes,
                    song.comment,
                    song_id if song_id is not None else song.id,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0

    def update_songs_data_batch(self, songs: list[SongVideoData]) -> bool:
        """
        楽曲を一括更新

        Args:
            songs: 更新する楽曲データのリスト

        Returns:
            bool: 更新に成功した場合True、楽曲が存在しない場合False
        """
        if len(songs) == 0:
            return False

        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            for song in songs:
                cursor.execute(
                    """
                    UPDATE songs SET
                        title = ?, publishedTimestamp = ?,
                        durationSeconds = ?, thumbnailURL = ?
                    WHERE id = ?
                """,
                    (
                        song.title,
                        song.publishedTimestamp,
                        song.durationSeconds,
                        song.thumbnailURL,
                        song.id,
                    ),
                )
            conn.commit()
            return cursor.rowcount > 0

    def delete_song(self, song_id: str) -> bool:
        """
        楽曲を削除

        Args:
            song_id: 削除する楽曲ID

        Returns:
            bool: 削除に成功した場合True、楽曲が存在しない場合False
        """
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.execute("DELETE FROM songs WHERE id = ?", (song_id,))
            conn.commit()
            return cursor.rowcount > 0

    def search_songs(self, **kwargs) -> list[Song]:
        """
        条件による楽曲検索

        Args:
            **kwargs: 検索条件（title, vocal, mainChord等）

        Returns:
            list[Song]: 条件に一致する楽曲のリスト
        """
        conditions = []
        params = []

        for key, value in kwargs.items():
            if value is None:
                continue

            if key in ["title", "comment"]:
                conditions.append(f"{key} LIKE ?")
                params.append(f"%{value}%")
            elif key in ["vocal", "illustrations", "movie"]:
                conditions.append(f"EXISTS (SELECT 1 FROM json_each({key}) WHERE json_each.value = ?)")
                params.append(value)
                # params.append(f'%"{value}"%')
            elif key in ["id", "mainChord", "mainKey", "publishedType"]:
                conditions.append(f"{key} = ?")
                params.append(value)

        if conditions:
            filter = "WHERE " + " AND ".join(conditions)
        else:
            filter = ""

        order = kwargs.get("order")
        # kwargsにNoneが入る可能性はある
        if order is None:
            order = "publishedTimestamp"

        is_asc = kwargs.get("asc", False)
        if is_asc is None:
            is_asc = False

        # orderとascはパラメータ化できない
        query = f"SELECT * FROM songs {filter} ORDER BY {order} {'ASC' if is_asc else 'DESC'}"

        logger.debug(f"Executing query: {query}")
        logger.debug(f"With parameters: {params}")

        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            return [Song(**row) for row in rows]

    def get_songs_count(self) -> int:
        """
        楽曲の総数を取得

        Returns:
            int: 楽曲の総数
        """
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM songs")
            return cursor.fetchone()[0]

    def add_songs_batch(self, songs: list[Song]) -> int:
        """
        複数の楽曲を一括追加

        Args:
            songs: 追加する楽曲データのリスト

        Returns:
            int: 追加に成功した楽曲数
        """
        success_count = 0
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            for song in songs:
                try:
                    conn.execute(
                        """
                        INSERT INTO songs (
                            id, title, publishedTimestamp, publishedType,
                            durationSeconds, thumbnailURL, vocal, illustrations, movie, bpm, mainKey,
                            chordRate6451, chordRate4561, mainChord, pianoRate,
                            modulationTimes, comment
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            song.id,
                            song.title,
                            song.publishedTimestamp,
                            song.publishedType,
                            song.durationSeconds,
                            song.thumbnailURL,
                            song.vocal,
                            song.illustrations,
                            song.movie,
                            song.bpm,
                            song.mainKey,
                            song.chordRate6451,
                            song.chordRate4561,
                            song.mainChord,
                            song.pianoRate,
                            song.modulationTimes,
                            song.comment,
                        ),
                    )
                    success_count += 1
                except sqlite3.IntegrityError:
                    # 既に存在する楽曲はスキップ
                    continue
            conn.commit()
        return success_count

    def clear_all_songs(self):
        """全楽曲を削除（デバッグ用）"""
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            conn.execute("DELETE FROM songs")
            conn.commit()

    def find_nearest_song(
        self,
        target: Song | str,
        limit: int = 10,
        parameters: Optional[SongsCustomParameters] = None,
        is_reversed: bool = False,
    ) -> list[SongInQueue]:
        """曲調の似た楽曲を取得

        Args:
            target (Song | str): 検索対象の楽曲または楽曲ID
            limit (int, optional): 楽曲の最大数。デフォルトは10。

        Raises:
            ValueError: 曲が見つからない場合、またはスコア計算に必要なデータが不足している場合

        Returns:
            list[Song]: 曲調の似た楽曲のリスト
        """
        if isinstance(target, str):
            target = self.get_song_by_id(target)
            if target is None:
                raise ValueError(f"Song with id {target} not found in database.")

        if target.score_can_be_calculated() is False:
            raise ValueError(f"Target song (ID: {target.id}) does not have enough data to calculate score.")

        queue = []
        for song in self.get_all_songs():
            if song == target:
                continue

            if not song.score_can_be_calculated():
                continue

            score = SongsMatchScore(song, target, self.std, parameters)
            heapq.heappush(queue, SongInQueue(song, score, is_reversed))

        return [heapq.heappop(queue) for _ in range(min(limit, len(queue)))]
