import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from db.songs_database import SongsDatabase
from db.update_youtube_data import regist_scheduler
from discordbot.bot import BackendDiscordClient, default_intents
from utils.config import ConfigStore, docs_description
from utils.auth import auth_initialize
from utils.youtube.api import OAuthClient
from utils.youtube.playlists import PlaylistManager
from utils.logger import logger, discord_handler
from routers import admin, general, search, songs, youtube


scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler
    app.state.db = SongsDatabase("db/data/songs.db")
    scheduler = regist_scheduler(app.state.db)

    auth_initialize()

    app.state.config_store = ConfigStore()

    youtube_oauth_client = OAuthClient()
    await youtube_oauth_client.start()
    app.state.playlist_manager = PlaylistManager(youtube_oauth_client)

    app.state.discord_client = BackendDiscordClient(intents=default_intents, command_prefix="!")
    discord_handler.init_bot(bot=app.state.discord_client)

    loop = asyncio.get_event_loop()
    loop.create_task(app.state.discord_client.start(config.discord_token))

    logger.info("Backend API started successfully.")
    yield
    if scheduler:
        scheduler.shutdown()

    await app.state.discord_client.close()


tags_metadata = [
    {
        "name": "General",
        "description": "APIに関する情報を取得",
    },
    {
        "name": "Songs",
        "description": "曲情報の取得・更新",
    },
    {
        "name": "Search",
        "description": "曲の検索",
    },
    {
        "name": "YouTube",
        "description": "YouTube関連の操作",
    },
    {"name": "Admin", "description": "管理者用(認証が必要)"},
]


app = FastAPI(
    title="MIMIさん全曲分析 バックエンドAPI",
    description=docs_description,
    version="0.1.0",
    # terms_of_service="https://takechi.f5.si/",
    contact={
        "name": "takechi",
        "url": "https://x.com/takechi_scratch/",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

# ConfigStoreは同期的に読み込む
config_store = ConfigStore()
# 内部の _config は __init__ で既に読み込まれている
config = config_store._config

if config is None:
    raise RuntimeError("Config not initialized.")

origins = [
    config.production_url if config.production_url else "http://localhost:3000",
    "http://localhost:8787",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)
app.include_router(general.router)
app.include_router(search.router)
app.include_router(songs.router)
app.include_router(youtube.router)

if __name__ == "__main__":
    if config.is_production:
        uvicorn.run(app, host="0.0.0.0", port=config.port)
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
