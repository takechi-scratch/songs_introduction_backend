# 前に使用していた、テスト用のCLIスクリプト
# 将来改修します

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
