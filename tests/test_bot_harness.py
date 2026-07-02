import asyncio
import importlib
import sys
from types import SimpleNamespace


def import_main(monkeypatch):
    monkeypatch.setenv("API_SERVICE_TOKEN", "test-token")
    monkeypatch.setenv("BACKEND_URL", "http://backend.test")
    monkeypatch.setenv("PUBLIC_URL", "http://public.test")
    monkeypatch.setenv("TOKEN", "discord-token")

    from discord.ext import commands

    monkeypatch.setattr(commands.Bot, "run", lambda self, token: None)
    sys.modules.pop("bot.main", None)
    sys.modules.pop("bot.apihelper.api", None)
    sys.modules.pop("bot.config", None)
    return importlib.import_module("bot.main")


def test_setup_hook_loads_python_extensions_and_installs_error_handler(monkeypatch):
    main = import_main(monkeypatch)
    bot = main.MyBot()
    loaded_extensions = []

    async def fake_load_extension(name):
        loaded_extensions.append(name)

    monkeypatch.setattr(main.os, "listdir", lambda path: ["poems.py", "README.md", "setup.py"])
    bot.load_extension = fake_load_extension

    asyncio.run(bot.setup_hook())

    assert loaded_extensions == ["bot.commands.poems", "bot.commands.setup"]
    assert bot.tree.on_error == bot.on_app_command_error


def test_on_message_replies_to_meow_and_processes_commands(monkeypatch):
    main = import_main(monkeypatch)
    bot = main.MyBot()
    sent_messages = []
    processed_messages = []

    async def fake_send(message):
        sent_messages.append(message)

    async def fake_process_commands(message):
        processed_messages.append(message)

    message = SimpleNamespace(
        author=SimpleNamespace(bot=False),
        content="please MEOW",
        channel=SimpleNamespace(send=fake_send),
    )
    bot.process_commands = fake_process_commands

    asyncio.run(bot.on_message(message))

    assert sent_messages == ["meow"]
    assert processed_messages == [message]


def test_on_message_ignores_bot_authors(monkeypatch):
    main = import_main(monkeypatch)
    bot = main.MyBot()
    processed_messages = []
    message = SimpleNamespace(
        author=SimpleNamespace(bot=True),
        content="meow",
        channel=SimpleNamespace(send=lambda message: None),
    )

    async def fake_process_commands(message):
        processed_messages.append(message)

    bot.process_commands = fake_process_commands

    asyncio.run(bot.on_message(message))

    assert processed_messages == []


def test_close_closes_api_session_before_bot_close(monkeypatch):
    main = import_main(monkeypatch)
    bot = main.MyBot()
    events = []

    async def fake_close_session():
        events.append("api")

    async def fake_bot_close(self):
        events.append("bot")

    monkeypatch.setattr(main, "close_session", fake_close_session)
    monkeypatch.setattr(main.commands.Bot, "close", fake_bot_close)

    asyncio.run(bot.close())

    assert events == ["api", "bot"]
