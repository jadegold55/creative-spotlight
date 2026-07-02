import importlib
import sys
from types import SimpleNamespace


def import_bot_module(monkeypatch, module_name):
    monkeypatch.setenv("API_SERVICE_TOKEN", "test-token")
    monkeypatch.setenv("BACKEND_URL", "http://backend.test")
    monkeypatch.setenv("PUBLIC_URL", "http://public.test")
    monkeypatch.setenv("TOKEN", "discord-token")
    sys.modules.pop(module_name, None)
    sys.modules.pop("bot.apihelper.api", None)
    sys.modules.pop("bot.config", None)
    return importlib.import_module(module_name)


class ResponseRecorder:
    def __init__(self):
        self.calls = []
        self.done = False

    async def defer(self, *args, **kwargs):
        self.done = True
        self.calls.append(("defer", args, kwargs))

    async def send_message(self, *args, **kwargs):
        self.done = True
        self.calls.append(("send_message", args, kwargs))

    async def edit_message(self, *args, **kwargs):
        self.done = True
        self.calls.append(("edit_message", args, kwargs))

    def is_done(self):
        return self.done


class FollowupRecorder:
    def __init__(self):
        self.calls = []

    async def send(self, *args, **kwargs):
        self.calls.append(("send", args, kwargs))


class FakeInteraction:
    def __init__(self, guild_id=42, user=None, guild=None, client=None):
        self.guild_id = guild_id
        self.user = user or SimpleNamespace(id=99, name="artist", bot=False)
        self.guild = guild if guild is not None else SimpleNamespace(id=guild_id)
        self.client = client or SimpleNamespace(get_cog=lambda name: None)
        self.response = ResponseRecorder()
        self.followup = FollowupRecorder()
        self.data = {}
