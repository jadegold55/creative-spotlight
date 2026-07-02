import asyncio
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytz

from tests.bot_test_helpers import FakeInteraction, import_bot_module


def test_next_daily_returns_future_utc_datetime(monkeypatch):
    daily = import_bot_module(monkeypatch, "bot.commands.daily")

    result = daily._next_daily(0, 0, pytz.timezone("America/New_York"))

    assert result.tzinfo == pytz.utc
    assert result > datetime.now(pytz.utc)


def test_send_poem_posts_poem_embed_to_configured_channel(monkeypatch):
    daily = import_bot_module(monkeypatch, "bot.commands.daily")
    channel = SimpleNamespace(send=AsyncMock())
    bot = SimpleNamespace(get_channel=lambda channel_id: channel)
    cog = daily.Daily(bot)

    def fake_scrape():
        return {"title": "Hope", "author": "Emily", "content": "Words"}

    monkeypatch.setattr(daily, "scrape", fake_scrape)

    asyncio.run(cog._send_poem({"guildId": 42, "poemChannelId": 123}))

    channel.send.assert_awaited_once()
    args, kwargs = channel.send.await_args
    assert args == ("@everyone",)
    assert kwargs["embed"].title == "Poem of the Day\n\nHope"
    assert "By Emily" in kwargs["embed"].description


def test_send_poem_skips_missing_channel(monkeypatch):
    daily = import_bot_module(monkeypatch, "bot.commands.daily")
    bot = SimpleNamespace(get_channel=lambda channel_id: None)
    cog = daily.Daily(bot)

    asyncio.run(cog._send_poem({"guildId": 42, "poemChannelId": 123}))


def test_poem_command_sends_embed_for_scraped_poem(monkeypatch):
    poems = import_bot_module(monkeypatch, "bot.commands.poems")
    cog = poems.Poetry(bot=SimpleNamespace())
    interaction = FakeInteraction()
    to_thread_calls = []

    async def fake_to_thread(func, *args, **kwargs):
        to_thread_calls.append((func, args, kwargs))
        return {"title": "Hope", "author": "Emily", "content": "Words"}

    monkeypatch.setattr(poems.asyncio, "to_thread", fake_to_thread)

    asyncio.run(
        poems.Poetry.poem.callback(
            cog,
            interaction,
            author="Emily Dickinson",
            title="Hope",
        )
    )

    assert to_thread_calls[0][2] == {
        "author": "Emily Dickinson",
        "title": "Hope",
    }
    call_name, args, kwargs = interaction.response.calls[-1]
    assert call_name == "send_message"
    assert args == ("Here's a poem by Emily",)
    assert kwargs["embed"].title == "Hope"


def test_poem_command_reports_scrape_failure(monkeypatch):
    poems = import_bot_module(monkeypatch, "bot.commands.poems")
    cog = poems.Poetry(bot=SimpleNamespace())
    interaction = FakeInteraction()

    async def fake_to_thread(func, *args, **kwargs):
        return None

    monkeypatch.setattr(poems.asyncio, "to_thread", fake_to_thread)

    asyncio.run(poems.Poetry.poem.callback(cog, interaction))

    assert interaction.response.calls[-1] == (
        "send_message",
        ("Sorry, I couldn't fetch a poem at the moment.",),
        {"ephemeral": True},
    )


def test_art_command_reports_missing_art_data(monkeypatch):
    art = import_bot_module(monkeypatch, "bot.commands.art")
    cog = art.Art(bot=SimpleNamespace())
    interaction = FakeInteraction()

    async def fake_to_thread(func, *args, **kwargs):
        return None

    monkeypatch.setattr(art.asyncio, "to_thread", fake_to_thread)

    asyncio.run(art.Art.random_art.callback(cog, interaction))

    assert interaction.response.calls[0] == (
        "defer",
        (),
        {"thinking": True, "ephemeral": True},
    )
    assert interaction.followup.calls[-1] == (
        "send",
        ("Sorry, I couldn't fetch a piece of art at the moment.",),
        {"ephemeral": True},
    )


def test_art_command_reports_image_download_failure(monkeypatch):
    art = import_bot_module(monkeypatch, "bot.commands.art")
    cog = art.Art(bot=SimpleNamespace())
    interaction = FakeInteraction()

    async def fake_to_thread(func, *args, **kwargs):
        return {
            "title": "Painting",
            "artist": "Artist",
            "date": "1900",
            "image_url": "http://image.test/art.jpg",
        }

    class FakeResponse:
        status = 503

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def read(self):
            return b""

    class FakeSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def get(self, url, headers=None):
            return FakeResponse()

    monkeypatch.setattr(art.asyncio, "to_thread", fake_to_thread)
    monkeypatch.setattr(art.aiohttp, "ClientSession", FakeSession)

    asyncio.run(art.Art.random_art.callback(cog, interaction))

    assert interaction.followup.calls[-1] == (
        "send",
        ("Couldn't download the art image.",),
        {"ephemeral": True},
    )
