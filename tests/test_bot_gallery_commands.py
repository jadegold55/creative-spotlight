import asyncio
from types import SimpleNamespace

from tests.bot_test_helpers import FakeInteraction, import_bot_module


def test_gallery_command_sends_empty_state(monkeypatch):
    gallery = import_bot_module(monkeypatch, "bot.commands.gallery")
    cog = gallery.Gallery(bot=SimpleNamespace())
    interaction = FakeInteraction(guild=SimpleNamespace(id=42))

    async def fake_get(path, params=None, headers=None):
        assert path == "images/all"
        assert params == {"guildId": 42}
        assert headers == {
            "X-User-Id": "99",
            "X-User-Name": "artist",
            "X-Command": "gallery",
        }
        return []

    monkeypatch.setattr(gallery, "get", fake_get)

    asyncio.run(gallery.Gallery.gallery.callback(cog, interaction))

    assert interaction.response.calls[0] == (
        "defer",
        (),
        {"thinking": True, "ephemeral": True},
    )
    assert interaction.followup.calls[-1] == (
        "send",
        ("The gallery is currently empty. Please check back later!",),
        {"ephemeral": True},
    )


def test_gallery_command_sends_grouped_view(monkeypatch):
    gallery = import_bot_module(monkeypatch, "bot.commands.gallery")
    cog = gallery.Gallery(bot=SimpleNamespace())
    interaction = FakeInteraction(guild=SimpleNamespace(id=42))
    images = [{"id": 1, "groupId": "a"}, {"id": 2, "groupId": "a"}]
    created_views = []

    class FakeGalleryViewer:
        def __init__(self, posts, user_id=None):
            self.posts = posts
            self.user_id = user_id
            created_views.append(self)

    async def fake_get(path, params=None, headers=None):
        return images

    monkeypatch.setattr(gallery, "get", fake_get)
    monkeypatch.setattr(gallery, "GalleryViewer", FakeGalleryViewer)

    asyncio.run(gallery.Gallery.gallery.callback(cog, interaction))

    assert created_views[0].posts == [[images[0], images[1]]]
    assert created_views[0].user_id == 99
    assert interaction.followup.calls[-1][2] == {
        "view": created_views[0],
        "ephemeral": True,
    }


def test_upload_rejects_non_image_attachment(monkeypatch):
    gallery = import_bot_module(monkeypatch, "bot.commands.gallery")
    cog = gallery.Gallery(bot=SimpleNamespace())
    interaction = FakeInteraction(guild=SimpleNamespace(id=42))
    attachment = SimpleNamespace(
        filename="notes.txt",
        content_type="text/plain",
        url="http://files.test/notes.txt",
    )

    asyncio.run(
        gallery.Gallery.upload.callback(
            cog,
            interaction,
            title="Sketch",
            file=attachment,
        )
    )

    assert interaction.followup.calls[-1] == (
        "send",
        ("`notes.txt` is not a valid image.",),
        {"ephemeral": True},
    )


def test_delete_command_sends_empty_state(monkeypatch):
    gallery = import_bot_module(monkeypatch, "bot.commands.gallery")
    cog = gallery.Gallery(bot=SimpleNamespace())
    interaction = FakeInteraction(guild=SimpleNamespace(id=42))

    async def fake_get(path, params=None, headers=None):
        assert path == "images/user/99"
        assert params == {"guildId": 42}
        assert headers == {"X-User-Id": "99"}
        return []

    monkeypatch.setattr(gallery, "get", fake_get)

    asyncio.run(gallery.Gallery.delete.callback(cog, interaction))

    assert interaction.followup.calls[-1] == (
        "send",
        ("You have no submissions to delete.",),
        {"ephemeral": True},
    )


def test_delete_view_edits_message_on_success(monkeypatch):
    gallery = import_bot_module(monkeypatch, "bot.commands.gallery")
    interaction = FakeInteraction()
    interaction.data = {"values": ["123"]}

    async def fake_delete(path, headers=None):
        assert path == "images/123"
        assert headers == {"X-User-Id": "99"}
        return 204, ""

    monkeypatch.setattr(gallery, "delete", fake_delete)

    async def exercise():
        view = gallery.DeleteView([])
        await view.on_select(interaction)

    asyncio.run(exercise())

    assert interaction.response.calls[-1] == (
        "edit_message",
        (),
        {"content": "Submission deleted!", "view": None},
    )


def test_delete_view_edits_message_on_failure(monkeypatch):
    gallery = import_bot_module(monkeypatch, "bot.commands.gallery")
    interaction = FakeInteraction()
    interaction.data = {"values": ["123"]}

    async def fake_delete(path, headers=None):
        return 500, "nope"

    monkeypatch.setattr(gallery, "delete", fake_delete)

    async def exercise():
        view = gallery.DeleteView([])
        await view.on_select(interaction)

    asyncio.run(exercise())

    assert interaction.response.calls[-1] == (
        "edit_message",
        (),
        {"content": "Failed to delete.", "view": None},
    )
