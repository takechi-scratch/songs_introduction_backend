# 設定情報を安全に保存するモジュール
# 一部ChatGPTで生成

import os
import json
import asyncio
from typing import Literal
from cryptography.fernet import Fernet
from pydantic import BaseModel

with open("assets/docs_description.md", "r", encoding="utf-8") as f:
    docs_description = f.read()


class Config(BaseModel):
    youtube_data_api_key: str
    official_channel_id: str
    is_production: bool
    production_url: str | None = None
    youtube_oauth_refresh_token: str | None = None
    youtube_oauth_client_id: str
    youtube_oauth_client_secret: str

    port: int = 8000

    user_roles: dict[str, Literal["admin", "editor", "user"]]


class ConfigStore:
    def __init__(self, path="config", key_path="secret.key"):
        self.path = path
        self.key_path = key_path
        self.lock = asyncio.Lock()
        self.crypto = self._load_crypto()
        self._config: Config | None = self._load_config()

    def _load_crypto(self):
        # 暗号鍵の読み込み or 生成
        if not os.path.exists(self.key_path):
            key = Fernet.generate_key()
            with open(self.key_path, "wb") as f:
                f.write(key)
        else:
            with open(self.key_path, "rb") as f:
                key = f.read()

        return Fernet(key)

    def _load_config(self) -> Config | None:
        # 設定ファイルが無い場合は None
        if not os.path.exists(self.path):
            return None

        with open(self.path, "rb") as f:
            encrypted = f.read()
            if not encrypted:
                return None

            try:
                decrypted = self.crypto.decrypt(encrypted)
                data = json.loads(decrypted.decode("utf-8"))
                return Config(**data)
            except Exception:
                # 復号失敗時はファイル破損など
                return None

    def _save(self):
        if self._config is None:
            return

        data = json.dumps(self._config.model_dump(), ensure_ascii=False).encode("utf-8")
        encrypted = self.crypto.encrypt(data)
        with open(self.path, "wb") as f:
            f.write(encrypted)

    async def set_config(self, config: Config):
        """設定全体を保存"""
        async with self.lock:
            self._config = config
            self._save()

    async def get_config(self) -> Config:
        """設定全体を取得"""
        async with self.lock:
            if self._config is None:
                raise ValueError("Config not initialized")
            return self._config

    async def update_config(self, **kwargs):
        """設定の一部を更新"""
        async with self.lock:
            if self._config is None:
                raise ValueError("Config not initialized")

            # 現在の設定を辞書に変換して更新
            current_data = self._config.model_dump()
            current_data.update(kwargs)
            self._config = Config(**current_data)
            self._save()


if __name__ == "__main__":
    import asyncio

    async def test():
        path = input("Config Path (default: config): ")
        key_path = input("Key Path (default: secret.key): ")
        store = ConfigStore(path if path else "config", key_path if key_path else "secret.key")
        if store._config is not None:
            print("Current Config:", await store.get_config())
        else:
            print("No existing config found. Creating new one.")

        youtube_data_api_key = input("YouTube Data API Key: ")
        official_channel_id = input("Official Channel ID: ")
        is_production = input("Is Production (yes/no): ").lower() == "yes"
        youtube_oauth_refresh_token = input("YouTube OAuth Refresh Token: ")
        youtube_oauth_client_id = input("YouTube OAuth Client ID: ")
        youtube_oauth_client_secret = input("YouTube OAuth Client Secret: ")
        user_roles = {}
        await store.set_config(
            Config(
                youtube_data_api_key=youtube_data_api_key,
                official_channel_id=official_channel_id,
                is_production=is_production,
                youtube_oauth_refresh_token=youtube_oauth_refresh_token,
                youtube_oauth_client_id=youtube_oauth_client_id,
                youtube_oauth_client_secret=youtube_oauth_client_secret,
                user_roles=user_roles,
            )
        )
        print("Config saved.")

    asyncio.run(test())
