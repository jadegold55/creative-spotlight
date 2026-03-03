import logging

import aiohttp
from bot.config import BACKEND_URL

log = logging.getLogger(__name__)

_session: aiohttp.ClientSession | None = None


async def _get_session() -> aiohttp.ClientSession:
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession()
    return _session


async def close_session():
    """Call on bot shutdown to cleanly close the session."""
    global _session
    if _session and not _session.closed:
        await _session.close()
        _session = None


async def get(path, params=None, headers=None):
    session = await _get_session()
    async with session.get(
        f"{BACKEND_URL}/{path}", params=params, headers=headers
    ) as response:
        if response.status == 200:
            return await response.json()
        else:
            log.warning(f"GET {path} returned {response.status}")
            return None


async def post(path, params=None, data=None, headers=None):
    session = await _get_session()
    async with session.post(
        f"{BACKEND_URL}/{path}", params=params, data=data, headers=headers
    ) as response:
        return response.status, await response.text()


async def delete(path, params=None, headers=None):
    session = await _get_session()
    async with session.delete(
        f"{BACKEND_URL}/{path}", params=params, headers=headers
    ) as response:
        return response.status, await response.text()
