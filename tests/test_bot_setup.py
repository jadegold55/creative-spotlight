import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from tests.bot_test_helpers import FakeInteraction, import_bot_module


def test_time_setup_confirm_requires_all_fields(monkeypatch):
    setup = import_bot_module(monkeypatch, "bot.commands.setup")
    interaction = FakeInteraction()

    async def exercise():
        view = setup.TimeSetupView(guild_id=42, channel_id=123, feature="poems")
        await setup.TimeSetupView.confirm(view, interaction, None)

    asyncio.run(exercise())

    assert interaction.response.calls == [
        (
            "send_message",
            ("Please fill in all fields before confirming.",),
            {"ephemeral": True},
        )
    ]


def test_time_setup_confirm_posts_poem_schedule(monkeypatch):
    setup = import_bot_module(monkeypatch, "bot.commands.setup")
    calls = []

    async def fake_post(path, params=None, headers=None):
        calls.append((path, params, headers))
        return 200, "ok"

    monkeypatch.setattr(setup, "post", fake_post)
    interaction = FakeInteraction()

    async def exercise():
        view = setup.TimeSetupView(guild_id=42, channel_id=123, feature="poems")
        view.hour = 12
        view.minute = 30
        view.period = "AM"
        view.timezone = "UTC"
        await setup.TimeSetupView.confirm(view, interaction, None)

    asyncio.run(exercise())

    assert calls == [
        (
            "guilds/42/setup-poems",
            {
                "poemChannelId": 123,
                "hour": 0,
                "minute": 30,
                "timezone": "UTC",
            },
            {"X-User-Id": "99", "X-User-Name": "artist"},
        )
    ]
    call_name, args, kwargs = interaction.response.calls[-1]
    assert call_name == "edit_message"
    assert "**Poems** configured!" in kwargs["content"]
    assert "Time: 12:30 AM (UTC)" in kwargs["content"]
    assert kwargs["embed"] is None
    assert kwargs["view"] is None


def test_time_setup_confirm_posts_contest_schedule_and_syncs(monkeypatch):
    setup = import_bot_module(monkeypatch, "bot.commands.setup")
    calls = []
    contest_cog = SimpleNamespace(sync_contest_for_guild=AsyncMock())
    client = SimpleNamespace(get_cog=lambda name: contest_cog if name == "Spotlight" else None)

    async def fake_post(path, params=None, headers=None):
        calls.append((path, params, headers))
        return 200, "ok"

    monkeypatch.setattr(setup, "post", fake_post)
    interaction = FakeInteraction(client=client)

    async def exercise():
        view = setup.TimeSetupView(
            guild_id=42,
            channel_id=456,
            feature="contest",
            day=5,
            duration=3,
        )
        view.hour = 7
        view.minute = 45
        view.period = "PM"
        view.timezone = "America/New_York"
        await setup.TimeSetupView.confirm(view, interaction, None)

    asyncio.run(exercise())

    assert calls == [
        (
            "guilds/42/setup-contest",
            {
                "spotlightChannelId": 456,
                "day": 5,
                "hour": 19,
                "minute": 45,
                "timezone": "America/New_York",
                "durationDays": 3,
            },
            {"X-User-Id": "99", "X-User-Name": "artist"},
        )
    ]
    contest_cog.sync_contest_for_guild.assert_awaited_once_with(42)
    assert "**Contest** configured!" in interaction.response.calls[-1][2]["content"]


def test_setup_remove_deletes_contest_setup_and_clears_scheduler(monkeypatch):
    setup = import_bot_module(monkeypatch, "bot.commands.setup")
    delete_calls = []
    contest_cog = SimpleNamespace(clear_contest_for_guild=AsyncMock())
    bot = SimpleNamespace(get_cog=lambda name: contest_cog if name == "Spotlight" else None)
    cog = setup.Setup(bot)
    interaction = FakeInteraction()
    feature = SimpleNamespace(value="contest", name="Contest")

    async def fake_delete(path, headers=None):
        delete_calls.append((path, headers))
        return 204, ""

    monkeypatch.setattr(setup, "delete", fake_delete)

    asyncio.run(setup.Setup.setup_remove.callback(cog, interaction, feature))

    assert delete_calls == [
        (
            "guilds/42/setup-contest",
            {"X-User-Id": "99", "X-Command": "SubCommandSetupRemove"},
        )
    ]
    contest_cog.clear_contest_for_guild.assert_awaited_once_with(42)
    assert interaction.response.calls[-1] == (
        "send_message",
        ("Contest configuration removed successfully!",),
        {"ephemeral": True},
    )


def test_setup_remove_reports_delete_failure(monkeypatch):
    setup = import_bot_module(monkeypatch, "bot.commands.setup")
    contest_cog = SimpleNamespace(clear_contest_for_guild=AsyncMock())
    bot = SimpleNamespace(get_cog=lambda name: contest_cog)
    cog = setup.Setup(bot)
    interaction = FakeInteraction()
    feature = SimpleNamespace(value="poems", name="Poems")

    async def fake_delete(path, headers=None):
        return 500, "nope"

    monkeypatch.setattr(setup, "delete", fake_delete)

    asyncio.run(setup.Setup.setup_remove.callback(cog, interaction, feature))

    contest_cog.clear_contest_for_guild.assert_not_called()
    assert interaction.response.calls[-1] == (
        "send_message",
        ("Failed to save settings. Please try again.",),
        {"ephemeral": True},
    )
