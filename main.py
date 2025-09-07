import asyncio


NATURAL_KEYS = {60, 62, 64, 65, 67, 69, 71}


class SongsDatabase:
    def __init__(self):
        self.songs = []
        self.songs_by_id = {}
        self.std = None

    async def fetch_songs(self, url: str) -> None:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            response = await client.get(url)

            # リダイレクトが発生した場合の確認
            # if response.history:
            #     print(f"Redirected from: {response.history[0].url}")
            #     print(f"Final URL: {response.url}")

            if not response.headers.get("Content-Type").startswith("application/json"):
                print(response.text)
                raise ValueError("Error in Google Apps Script")

            for item in response.json():
                song = Song(**item)
                self.songs.append(song)
                self.songs_by_id[song.id] = song

            print("Data received:", self.songs)

        self.std = SongsSTD(self.songs)

    def find_nearest_song(self, target: Song | str, limit: int = 10) -> list[Song]:
        if isinstance(target, str):
            target = self.songs_by_id.get(target)
            if not target:
                raise ValueError(f"Song with id {target} not found in database.")

        queue = []
        for song in self.songs:
            if song == target:
                continue

            score = SongsMatchScore(song, target, self.std)
            heapq.heappush(queue, SongInQueue(song, score))

        return [(song_in_queue.song, song_in_queue.score) for song_in_queue in [heapq.heappop(queue) for _ in range(min(limit, len(queue)))]]



async def main():
    db = SongsDatabase()
    url = "https://script.google.com/macros/s/AKfycbx-qahGzAdW4w5KvG3n7QkLWmZRxucywd7TrrTWkGYzlIJ65fCHD02XlivkrZBhEYY5cw/exec"
    await db.fetch_songs(url)

    while True:
        query = input("1: find nearest songs\n2: find nearest songs(includes repr)\n3: calculate SongsMatchScore\n>>>")
        if query == "1" or query == "2":
            id = input("Enter song ID to find nearest songs (or 'exit' to quit): ")
            if id.lower() == 'exit':
                break

            try:
                nearest_songs = db.find_nearest_song(id)
                print("Nearest songs found:")
                for song, match_score in nearest_songs:
                    if query == "1":
                        print(f" - {song.title} (Score: {str(match_score)})")
                    elif query == "2":
                        print(f" - {song.title} (Score: {str(match_score)} repr: {repr(match_score)})")
            except ValueError as e:
                print(e)

        elif query == "3":
            id1 = input("Enter first song ID: ")
            id2 = input("Enter second song ID: ")

            song1 = db.songs_by_id.get(id1)
            song2 = db.songs_by_id.get(id2)

            if not song1 or not song2:
                print("One or both songs not found in database.")
                continue

            match_score = SongsMatchScore(song1, song2, db.std)
            print(f"SongsMatchScore between {song1.title} and {song2.title}: {match_score}")
            print(f"repr: {repr(match_score)}")

        else:
            exit()

asyncio.run(main())
