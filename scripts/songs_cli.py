# テスト用のCLIスクリプト
import asyncio

from src.db.songs_database import SongsDatabase
from src.utils.songs_class import SongsMatchScore, Song


class SongsCLI:
    def __init__(self, db: SongsDatabase):
        self.db = db

    def _find_nearest_song(self, includes_repr: bool = False):
        id = input("Enter song ID to find nearest songs (or 'exit' to quit): ")
        if id.lower() == "exit":
            exit()

        try:
            nearest_songs = self.db.find_nearest_song(id)
            print("Nearest songs found:")
            for song_queue in nearest_songs:
                song, match_score = song_queue.song, song_queue.score
                if includes_repr:
                    print(f" - {song.title} (Score: {str(match_score)} repr: {repr(match_score)})")
                else:
                    print(f" - {song.title} (Score: {str(match_score)})")
        except ValueError as e:
            print(e)

    def _calculate_songs_match_score(self):
        id1 = input("Enter first song ID: ")
        id2 = input("Enter second song ID: ")

        song1 = self.db.get_song_by_id(id1)
        song2 = self.db.get_song_by_id(id2)

        if not song1 or not song2:
            print("One or both songs not found in database.")
            return

        match_score = SongsMatchScore(song1, song2, self.db.std)
        print(f"SongsMatchScore between {song1.title} and {song2.title}: {match_score}")
        print(f"repr: {repr(match_score)}")

    def _add_song(self):
        # 使い勝手があまりよくない
        fields = [
            "id",
            "title",
            "publishedType",
            "vocal",
            "illustrations",
            "movie",
            "bpm",
            "mainKey",
            "chordRate6451",
            "chordRate4561",
            "mainChord",
            "pianoRate",
            "modulationTimes",
            "comment",
        ]

        new_song = {}
        for field in fields:
            print(f"{field}: ", end="")
            value = input().strip()
            if value == "":
                value = None
            new_song[field] = value
        try:
            self.db.add_song(Song(**new_song))
            print(f"Song {new_song['title']} added successfully.")
        except ValueError as e:
            print(e)

    def run(self):
        menu = [
            "Find nearest songs",
            "Find nearest songs (includes repr)",
            "Calculate SongsMatchScore",
            "Add song",
            "Exit",
        ]
        while True:
            query = input("\n".join(f"{i+1}. {item}" for i, item in enumerate(menu)) + "\n>>> ")
            if query == "1" or query == "2":
                self._find_nearest_song(includes_repr=(query == "2"))

            elif query == "3":
                self._calculate_songs_match_score()

            elif query == "4":
                self._add_song()

            elif query == "5" or query.lower() == "exit":
                exit()


async def main():
    songs_cli = SongsCLI(SongsDatabase())
    songs_cli.run()


if __name__ == "__main__":
    asyncio.run(main())
