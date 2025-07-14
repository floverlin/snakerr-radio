from .utils import Downloaded, valid_size, get_temp_filename

import aiohttp
import aiofiles
import os


async def _dowload_song(link: str, session: aiohttp.ClientSession):
    async with session.get(link) as resp:
        if not check_mp3(resp):
            raise Exception
        content = await resp.read()
    filepath = await get_temp_filename()
    async with aiofiles.open(filepath, "wb") as file:
        await file.write(content)

    if not valid_size(os.path.getsize(filepath)):
        return None
    return Downloaded(filepath)


async def download(link: str) -> Downloaded | None:
    try:
        async with aiohttp.ClientSession() as session:
            return await _dowload_song(link, session)
    except Exception:
        return None


def check_mp3(resp: aiohttp.ClientResponse) -> bool:
    types = [
        "audio/mpeg",
        "audio/mp3",
    ]
    return resp.status == 200
