from urllib import parse

from src.utils.config import ConfigStore


async def including_video_id(text: str | None) -> str | None:
    """Extracts the video ID from a YouTube URL if present."""
    if text is None or text.strip() == "":
        return None

    config = await ConfigStore().get_config()
    production_hostname = None
    if config.production_url:
        try:
            parsed_url = parse.urlparse(config.production_url)
            production_hostname = parsed_url.hostname
        except Exception:
            pass

    try:
        parsed_url = parse.urlparse(text)
        if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
            if parsed_url.path.startswith("/shorts/"):
                # ショートのURL
                return parsed_url.path.split("/shorts/")[1]

            # 通常の動画URL
            query_params = parse.parse_qs(parsed_url.query)
            return query_params.get("v", [None])[0]
        elif parsed_url.hostname == "youtu.be":
            # 短縮URL
            return parsed_url.path[1:].split("/")[0]  # Remove the leading '/'
        elif parsed_url.hostname == production_hostname and parsed_url.path.startswith("/songs/"):
            # MIMIさん全曲紹介のURL
            return parsed_url.path.split("/songs/")[1]
    except Exception:
        pass

    # IDのみの入力
    if len(text) == 11 and all(c.isalnum() or c in ["-", "_"] for c in text):
        return text

    return None
