import aiofiles.os as aios
import os

from asyncio.locks import Lock

from aiogram.types import FSInputFile

lock = Lock()
TEMP = "./temp"
FILENAME = "tempfile"

os.makedirs(TEMP, exist_ok=True)


async def get_temp_filename(*, split: bool = False) -> tuple[str, str] | str:
    await lock.acquire()
    filename = await _get_filename()
    lock.release()
    if split:
        return TEMP, filename
    return f"{TEMP}/{FILENAME}"


async def _get_filename() -> str:
    files = await aios.listdir(TEMP)
    numbers = [int(file.split("(")[1][:-1]) for file in files]
    index = 0
    if numbers:
        index = max(numbers)
    return FILENAME + "(" + str(index) + ")"


class Downloaded:
    def __init__(self, filepath: str, title: str = "title", artist: str = "artist"):
        self.file = FSInputFile(filepath)
        self.title, self.artist = title, artist

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await aios.remove(self.file.path)


def valid_size(size: int):
    if size > 50 * 1024 * 1024:
        return False
    return True
