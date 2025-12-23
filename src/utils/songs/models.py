from typing import Optional

from pydantic import BaseModel

NATURAL_KEYS = {60, 62, 64, 65, 67, 69, 71}


class SongVideoData(BaseModel):
    id: str
    title: str
    publishedTimestamp: int
    durationSeconds: Optional[int] = None
    thumbnailURL: Optional[str] = None


class Song(SongVideoData):
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
    lyricsOfficiallyReleased: bool = False
    comment: Optional[str] = None

    def __eq__(self, value):
        if isinstance(value, Song):
            return self.id == value.id
        elif isinstance(value, str):
            return self.id == value
        else:
            return NotImplemented

    def score_can_be_calculated(self) -> bool:
        return (
            self.vocal is not None
            and self.illustrations is not None
            and self.movie is not None
            and self.bpm is not None
            and self.mainKey is not None
            and self.chordRate6451 is not None
            and self.chordRate4561 is not None
            and self.mainChord is not None
            and self.pianoRate is not None
            and self.modulationTimes is not None
        )
