import yt_dlp
import logging

from .utils import get_temp_filename, Downloaded


async def download(url):
    try:
        filepath = await get_temp_filename()

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": filepath,
            "quiet": False,
            "no_warnings": False,
            "skip_fragments": False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "Unknown Title")
            uploader = info.get("uploader", "Unknown Artist")

        # os.rename(path + ".mp3", path)
        return Downloaded(filepath, title, uploader)

    except Exception as e:
        logging.error(f"Ошибка при скачивании через yt-dlp: {e}")
        return None
