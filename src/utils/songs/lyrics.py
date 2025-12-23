import numpy as np

from .models import Song


class LyricsVecManager:
    def __init__(self, songs: list[Song]):
        self.max_similarity = 0.0
        self.min_similarity = 0.0

        for song_1 in songs:
            for song_2 in songs:
                if song_1 == song_2:
                    continue

                if song_1.lyricsVector is None or song_2.lyricsVector is None:
                    continue

                if not self._has_lyrics(song_1.lyricsVector) or not self._has_lyrics(song_2.lyricsVector):
                    continue

                # コサイン類似度の計算
                sim = np.dot(song_1.lyricsVector, song_2.lyricsVector) / (
                    np.linalg.norm(song_1.lyricsVector) * np.linalg.norm(song_2.lyricsVector)
                )
                if sim > self.max_similarity:
                    self.max_similarity = sim
                if sim < self.min_similarity:
                    self.min_similarity = sim

    def lyrics_similarity(self, song_1: "Song", song_2: "Song") -> float:
        if song_1.lyricsVector is None or song_2.lyricsVector is None:
            return 0.0

        if not self._has_lyrics(song_1.lyricsVector) or not self._has_lyrics(song_2.lyricsVector):
            if not self._has_lyrics(song_1.lyricsVector) and not self._has_lyrics(song_2.lyricsVector):
                return 1.0

            return -1.0

        sim = np.dot(song_1.lyricsVector, song_2.lyricsVector) / (
            np.linalg.norm(song_1.lyricsVector) * np.linalg.norm(song_2.lyricsVector)
        )

        # Min-Max正規化で-1~1の範囲に変換
        if self.max_similarity == self.min_similarity:
            return 0.0
        return 2 * (sim - self.min_similarity) / (self.max_similarity - self.min_similarity) - 1

    def _has_lyrics(self, vector: list[float]) -> bool:
        return not all(x == 0 for x in vector)


if __name__ == "__main__":
    # TODO: おそらく循環インポートなので修正
    from src.db.songs_database import SongsDatabase

    db = SongsDatabase()
    lyrics_vec_manager = LyricsVecManager(db.get_all_songs())

    song_1 = db.get_song_by_id(input("Song ID 1: "))
    song_2 = db.get_song_by_id(input("Song ID 2: "))
    sim = lyrics_vec_manager.lyrics_similarity(song_1, song_2)
    print(f"Lyrics Similarity: {sim}")
