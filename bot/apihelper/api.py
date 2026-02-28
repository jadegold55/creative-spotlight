import aiohttp
from bot.config import BACKEND_URL


async def get(path, params=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BACKEND_URL}/{path}", params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None


async def post(path, params=None, data=None):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BACKEND_URL}/{path}", params=params, data=data
        ) as response:
            return response.status, await response.text()


async def delete(path, params=None):
    async with aiohttp.ClientSession() as session:
        async with session.delete(f"{BACKEND_URL}/{path}", params=params) as response:
            return response.status, await response.text()
