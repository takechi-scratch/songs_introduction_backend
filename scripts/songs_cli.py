# テスト用のCLIスクリプト
import asyncio

from db.songs_database import SongsDatabase
from utils.songs_class import SongsMatchScore


async def main():
    db = SongsDatabase()
    while True:
        query = input("1: find nearest songs\n2: find nearest songs(includes repr)\n3: calculate SongsMatchScore\n>>>")
        if query == "1" or query == "2":
            id = input("Enter song ID to find nearest songs (or 'exit' to quit): ")
            if id.lower() == "exit":
                break

            try:
                nearest_songs = db.find_nearest_song(id)
                print("Nearest songs found:")
                for song_queue in nearest_songs:
                    song, match_score = song_queue.song, song_queue.score
                    if query == "1":
                        print(f" - {song.title} (Score: {str(match_score)})")
                    elif query == "2":
                        print(f" - {song.title} (Score: {str(match_score)} repr: {repr(match_score)})")
            except ValueError as e:
                print(e)

        elif query == "3":
            id1 = input("Enter first song ID: ")
            id2 = input("Enter second song ID: ")

            song1 = db.get_song_by_id(id1)
            song2 = db.get_song_by_id(id2)

            if not song1 or not song2:
                print("One or both songs not found in database.")
                continue

            match_score = SongsMatchScore(song1, song2, db.std)
            print(f"SongsMatchScore between {song1.title} and {song2.title}: {match_score}")
            print(f"repr: {repr(match_score)}")

        else:
            exit()


if __name__ == "__main__":
    asyncio.run(main())
