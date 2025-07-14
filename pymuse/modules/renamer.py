from aiogram import Bot

from .utils import get_temp_filename, Downloaded

from config import config

import aiofiles
import aiohttp


async def rename(file_id: str):
    async with Bot(config.token) as bot:
        file = await bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"

    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as resp:
            if resp.status != 200:
                raise Exception("download error in renamer")
            filepath = await get_temp_filename()
            async with aiofiles.open(filepath, "wb") as file:
                await file.write(await resp.read())

    return Renamed(filepath)


class Renamed(Downloaded):
    def __init__(self, filepath: str):
        super().__init__(filepath, "renamed", "renamed")
