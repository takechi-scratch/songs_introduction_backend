import httpx

from src.db.songs_database import SongsDatabase
from src.utils.songs_class import Song


async def fetch_songs(url: str, database_path: str = "data/songs.db") -> None:
    database = SongsDatabase(database_path)

    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        response = await client.get(url)

        if not response.headers.get("Content-Type").startswith("application/json"):
            print(response.text)
            raise ValueError("Error in Google Apps Script")

        database.add_songs_batch(
            [Song(**item, thumbnailURL="https://example.com/thumbnail.jpg") for item in response.json()]
        )

        print("Data received:", database.get_all_songs())


if __name__ == "__main__":
    url = "https://script.google.com/macros/s/AKfycbx-qahGzAdW4w5KvG3n7QkLWmZRxucywd7TrrTWkGYzlIJ65fCHD02XlivkrZBhEYY5cw/exec"
    import asyncio

    asyncio.run(fetch_songs(url))
