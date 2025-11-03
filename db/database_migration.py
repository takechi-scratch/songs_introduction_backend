# データベース移行用のスクリプト

from db.songs_database import SongsDatabase
import json

from utils.songs_class import Song


def export_songs(database_path: str = "db/data/songs.db", output_path: str = "exported_songs.json") -> None:
    database = SongsDatabase(database_path)
    songs = database.get_all_songs()
    songs_data = [song.model_dump() for song in songs]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(songs_data, f, ensure_ascii=False, indent=4)

    print(f"Exported {len(songs_data)} songs to {output_path}")


def load_songs_into_v2(
    database_path: str = "db/data/songs.db", input_path: str = "db/data/exported_songs.json"
) -> None:
    database = SongsDatabase(database_path)

    with open(input_path, "r", encoding="utf-8") as f:
        songs = json.load(f)

    database.add_songs_batch(
        [
            Song(
                id=song["id"],
                title=song["title"],
                publishedTimestamp=song["publishedTimestamp"],
                durationSeconds=song["durationSeconds"],
                thumbnailURL=song.get("thumbnailURL") if song.get("thumbnailURL") != "" else None,
                publishedType=song["publishedType"],
                vocal=(
                    [x.strip() for x in song.get("vocal").split("/") if x.strip() != ""]
                    if song.get("vocal") is not None
                    else None
                ),
                illustrations=(
                    [x.strip() for x in song.get("illustrations").split("/") if x.strip() != ""]
                    if song.get("illustrations") is not None
                    else None
                ),
                movie=(
                    [x.strip() for x in song.get("movie").split("/") if x.strip() != ""]
                    if song.get("movie") is not None
                    else None
                ),
                bpm=song.get("bpm"),
                mainKey=song.get("mainKey"),
                chordRate6451=song.get("chordRate6451"),
                chordRate4561=song.get("chordRate4561"),
                mainChord=song.get("mainChord"),
                pianoRate=song.get("pianoRate"),
                modulationTimes=song.get("modulationTimes"),
                comment=song.get("comment"),
            )
            for song in songs
        ]
    )

    print(f"Loaded {len(songs)} songs into version 2")
