import asyncio
import sys
import types
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytz

from tests.bot_test_helpers import FakeInteraction, import_bot_module


def import_contest(monkeypatch):
    apscheduler = types.ModuleType("apscheduler")
    schedulers = types.ModuleType("apscheduler.schedulers")
    asyncio_scheduler = types.ModuleType("apscheduler.schedulers.asyncio")
    asyncio_scheduler.AsyncIOScheduler = FakeAsyncIOScheduler
    monkeypatch.setitem(sys.modules, "apscheduler", apscheduler)
    monkeypatch.setitem(sys.modules, "apscheduler.schedulers", schedulers)
    monkeypatch.setitem(sys.modules, "apscheduler.schedulers.asyncio", asyncio_scheduler)
    return import_bot_module(monkeypatch, "bot.commands.contest")


class FakeGuild:
    def __init__(self, member=None):
        self.member = member

    def get_member(self, user_id):
        return self.member

    async def fetch_member(self, user_id):
        return self.member


class FakeScheduler:
    def __init__(self):
        self.jobs = {}
        self.running = False

    def add_job(self, func, trigger, run_date=None, id=None, replace_existing=False, kwargs=None):
        self.jobs[id] = {
            "func": func,
            "trigger": trigger,
            "run_date": run_date,
            "replace_existing": replace_existing,
            "kwargs": kwargs,
        }

    def get_job(self, job_id):
        return self.jobs.get(job_id)

    def get_jobs(self):
        return list(self.jobs.values())


class FakeAsyncIOScheduler(FakeScheduler):
    def __init__(self, timezone=None):
        super().__init__()
        self.timezone = timezone

    def start(self):
        self.running = True

    def shutdown(self, wait=False):
        self.running = False


def test_parse_utc_datetime_accepts_zulu_and_naive_values(monkeypatch):
    contest = import_contest(monkeypatch)

    zulu = contest._parse_utc_datetime("2026-04-03T21:00:00Z")
    naive = contest._parse_utc_datetime("2026-04-03T21:00:00")

    assert zulu.tzinfo == pytz.utc
    assert naive.tzinfo == pytz.utc
    assert contest._format_discord_timestamp(zulu) == "<t:1775250000:F>"
    assert contest._parse_utc_datetime(None) is None


def test_signup_view_rejects_dm_interaction(monkeypatch):
    interaction = FakeInteraction()
    interaction.guild = None

    async def exercise():
        contest = import_contest(monkeypatch)
        view = contest.ContestSignupView(bot=SimpleNamespace(), guild_id=42)
        await view._on_signup(interaction)

    asyncio.run(exercise())

    assert interaction.response.calls == [
        (
            "send_message",
            ("Contest signups can only be used inside the server.",),
            {"ephemeral": True},
        )
    ]


def test_signup_view_withdraws_existing_signup(monkeypatch):
    contest = import_contest(monkeypatch)
    api_calls = []
    member = SimpleNamespace(pending=False)
    interaction = FakeInteraction(guild=FakeGuild(member))

    async def fake_get(path, headers=None):
        api_calls.append(("get", path, headers))
        return [{"userId": 99}]

    async def fake_delete(path, params=None, headers=None):
        api_calls.append(("delete", path, params, headers))
        return 204, ""

    monkeypatch.setattr(contest, "get", fake_get)
    monkeypatch.setattr(contest, "delete", fake_delete)

    async def exercise():
        view = contest.ContestSignupView(bot=SimpleNamespace(), guild_id=42)
        await view._on_signup(interaction)

    asyncio.run(exercise())

    assert api_calls[-1] == (
        "delete",
        "contest_signups/42/signup",
        {"userId": 99},
        {"X-User-Id": "99", "X-User-Name": "artist"},
    )
    assert interaction.response.calls[-1] == (
        "send_message",
        ("You have withdrawn from the contest.",),
        {"ephemeral": True},
    )


def test_signup_view_posts_verified_signup(monkeypatch):
    contest = import_contest(monkeypatch)
    api_calls = []
    member = SimpleNamespace(pending=False)
    interaction = FakeInteraction(guild=FakeGuild(member))

    async def fake_get(path, headers=None):
        api_calls.append(("get", path, headers))
        return []

    async def fake_post(path, params=None, headers=None):
        api_calls.append(("post", path, params, headers))
        return 201, ""

    monkeypatch.setattr(contest, "get", fake_get)
    monkeypatch.setattr(contest, "post", fake_post)

    async def exercise():
        view = contest.ContestSignupView(bot=SimpleNamespace(), guild_id=42)
        await view._on_signup(interaction)

    asyncio.run(exercise())

    assert api_calls[-1] == (
        "post",
        "contest_signups/42/signup",
        {"userId": 99, "username": "artist", "isVerified": "true"},
        {"X-User-Id": "99", "X-User-Name": "artist"},
    )
    assert interaction.response.calls[-1] == (
        "send_message",
        ("You're signed up. Upload your entry with `/upload` before the deadline.",),
        {"ephemeral": True},
    )


def test_sync_contest_for_guild_schedules_start_and_end_jobs(monkeypatch):
    contest = import_contest(monkeypatch)
    bot = SimpleNamespace(user=SimpleNamespace(id=7), add_view=lambda view: None)
    spotlight = contest.Spotlight(bot)
    spotlight.scheduler = FakeScheduler()
    start = datetime.now(pytz.utc) + timedelta(hours=1)
    end = start + timedelta(days=3)
    guild = {
        "guildId": 42,
        "spotlightChannelId": 123,
        "contestStartAt": start.isoformat(),
        "contestDeadlineAt": end.isoformat(),
    }

    asyncio.run(spotlight.sync_contest_for_guild(42, guild))

    assert 42 in spotlight.registered_signup_views
    assert "contest:42:start" in spotlight.scheduler.jobs
    assert "contest:42:end" in spotlight.scheduler.jobs
    assert spotlight.scheduler.jobs["contest:42:start"]["kwargs"] == {"guild": guild}
    assert spotlight.scheduler.jobs["contest:42:end"]["kwargs"] == {"guild": guild}


def test_start_contest_sends_signup_view_and_tracks_active_contest(monkeypatch):
    contest = import_contest(monkeypatch)
    channel = SimpleNamespace(send=AsyncMock())
    bot = SimpleNamespace(
        user=SimpleNamespace(id=7),
        add_view=lambda view: None,
        get_channel=lambda channel_id: channel,
    )
    spotlight = contest.Spotlight(bot)
    deadline = datetime.now(pytz.utc) + timedelta(days=1)
    guild = {
        "guildId": 42,
        "spotlightChannelId": 123,
        "contestDeadlineAt": deadline.isoformat(),
    }

    async def exercise():
        await spotlight._start_contest(guild)

    asyncio.run(exercise())

    channel.send.assert_awaited_once()
    assert 42 in spotlight.active_contests
    args, kwargs = channel.send.await_args
    assert args == ()
    assert kwargs["embed"].title == "Artist Showcase"
    assert isinstance(kwargs["view"], contest.ContestSignupView)
