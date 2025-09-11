from pydantic import BaseModel
import statistics
from functools import total_ordering

from utils.math import sigmoid

NATURAL_KEYS = {60, 62, 64, 65, 67, 69, 71}

class SongVideoData(BaseModel):
    id: str
    title: str
    publishedTimestamp: int
    isPublishedInOriginalChannel: bool
    durationSeconds: int
    thumbnailURL: str

class Song(SongVideoData):
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


class SongsSTD:
    def __init__(self, songs: list[Song]):
        self.songs = songs
        self.bpm = statistics.pstdev(song.bpm for song in songs)
        self.chordRate6451 = statistics.pstdev(song.chordRate6451 for song in songs)
        self.chordRate4561 = statistics.pstdev(song.chordRate4561 for song in songs)
        self.pianoRate = statistics.pstdev(song.pianoRate for song in songs)


class SongInQueue:
    def __init__(self, song: Song, score: "SongsMatchScore"):
        self.song = song
        self.score = score

    def __lt__(self, other):
        return -float(self.score) < -float(other.score)

    def __eq__(self, other):
        return self.song == other.song


@total_ordering
class SongsMatchScore:
    def __init__(self, song1: Song, song2: Song, songs_std: SongsSTD, **kwargs) -> None:
        self.song1 = song1
        self.song2 = song2
        self.songs_std = songs_std

        if kwargs:
            [self.__setattr__(key, value) for key, value in kwargs.items()]
        else:
            self._calculate_diff()
            self._moderate()

    def _calculate_diff(self) -> None:
        song1, song2, songs_std = self.song1, self.song2, self.songs_std

        if song1.vocal == song2.vocal:
            if song1.vocal in {"初音ミク", "可不", "重音テトSV"}:
                self.vocal = 0.3
            else:
                # "-"（なし）もこっちに含む
                self.vocal = 1.0
        else:
            self.vocal = 0.0

        self.illustrations = int(song1.illustrations == song2.illustrations)
        self.movie = int(song1.movie == song2.movie)

        bpm_raw = 1.0 - abs(song1.bpm - song2.bpm) / songs_std.bpm
        bpm_doubled = 1.0 - abs(max(song1.bpm, song2.bpm) - 2 * min(song1.bpm, song2.bpm)) / songs_std.bpm
        self.bpm = max(bpm_raw, bpm_doubled * 0.5)

        self.chordRate6451 = 1.0 - abs(song1.chordRate6451 - song2.chordRate6451) / songs_std.chordRate6451
        self.chordRate4561 = 1.0 - abs(song1.chordRate4561 - song2.chordRate4561) / songs_std.chordRate4561
        self.pianoRate = 1.0 - abs(song1.pianoRate - song2.pianoRate) / songs_std.pianoRate

        self.mainKey = 0.0
        if song1.mainKey == song2.mainKey:
            self.mainKey = 1.0
        elif abs(song1.mainKey - song2.mainKey) == 1:
            self.mainKey = 0.4
        elif song1.mainKey * song2.mainKey < 0:
            self.mainKey = -1.0
        elif int(song1.mainKey in NATURAL_KEYS) == int(song2.mainKey in NATURAL_KEYS):
            self.mainKey = 0.3
        elif abs(song1.mainKey - song2.mainKey) <= 2 and song1.mainKey not in NATURAL_KEYS and song2.mainKey not in NATURAL_KEYS:
            self.mainKey = 0.7

        self.mainChord = -1.0
        if song1.mainChord != "" and song2.mainChord != "":
            if song1.mainChord == song2.mainChord:
                self.mainChord = 1.0
            elif song1.mainChord[0] == song2.mainChord[0]:
                self.mainChord = 0.7

        self.modulationTimes = 1.0 - abs(min(3, song1.modulationTimes) - min(3, song2.modulationTimes)) * 0.6

    def _moderate(self) -> None:
        """Moderate the values to be within the range [-1, 1].
        """
        self.vocal = max(-1, min(1, round(self.vocal, 4)))
        self.illustrations = max(-1, min(1, round(self.illustrations, 4)))
        self.movie = max(-1, min(1, round(self.movie, 4)))
        self.bpm = max(-1, min(1, round(self.bpm, 4)))
        self.chordRate6451 = max(-1, min(1, round(self.chordRate6451, 4)))
        self.chordRate4561 = max(-1, min(1, round(self.chordRate4561, 4)))
        self.pianoRate = max(-1, min(1, round(self.pianoRate, 4)))
        self.mainKey = max(-1, min(1, round(self.mainKey, 4)))
        self.mainChord = max(-1, min(1, round(self.mainChord, 4)))
        self.modulationTimes = max(-1, min(1, round(self.modulationTimes, 4)))

    def get_score(self) -> float:
        return sigmoid(
            self.vocal * 0.8
            + self.illustrations
            + self.movie * 0.3
            + self.bpm * 1.3
            + max(self.chordRate6451, self.chordRate4561) * 0.5
            + min(self.chordRate6451, self.chordRate4561) * 0.1
            + self.pianoRate * 0.6  # かなり差が大きいので小さめ
            + self.mainKey * 0.6
            + self.mainChord * 0.6
            + self.modulationTimes * 0.4
        , a=0.7)

    def __str__(self) -> str:
        return f"{self.get_score() * 100:.2f}%"

    def __repr__(self):
        return f"SongsMatchScore(vocal={self.vocal}, illustrations={self.illustrations}, movie={self.movie}, bpm={self.bpm}, chordRate6451={self.chordRate6451}, chordRate4561={self.chordRate4561}, pianoRate={self.pianoRate}, mainKey={self.mainKey}, mainChord={self.mainChord}, modulationTimes={self.modulationTimes})"

    def __float__(self) -> float:
        return self.get_score()

    def __add__(self, other):
        return float(self) + float(other)

    def __sub__(self, other):
        return float(self) - float(other)

    def __mul__(self, other):
        return float(self) * float(other)

    def __truediv__(self, other):
        return float(self) / float(other)

    def __lt__(self, other):
        return float(self) < float(other)

    def __eq__(self, other):
        return float(self) == float(other)
