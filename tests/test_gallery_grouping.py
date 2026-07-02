import importlib
import sys


def import_gallery(monkeypatch):
    monkeypatch.setenv("API_SERVICE_TOKEN", "test-token")
    monkeypatch.setenv("BACKEND_URL", "http://backend.test")
    monkeypatch.setenv("PUBLIC_URL", "http://public.test")
    sys.modules.pop("bot.commands.gallery", None)
    sys.modules.pop("bot.apihelper.api", None)
    sys.modules.pop("bot.config", None)
    return importlib.import_module("bot.commands.gallery")


def test_group_images_into_posts_uses_group_id_and_preserves_order(monkeypatch):
    gallery = import_gallery(monkeypatch)
    images = [
        {"id": 1, "groupId": "a", "title": "first"},
        {"id": 2, "groupId": "b", "title": "second"},
        {"id": 3, "groupId": "a", "title": "third"},
    ]

    posts = gallery.group_images_into_posts(images)

    assert posts == [
        [
            {"id": 1, "groupId": "a", "title": "first"},
            {"id": 3, "groupId": "a", "title": "third"},
        ],
        [{"id": 2, "groupId": "b", "title": "second"}],
    ]


def test_group_images_into_posts_falls_back_to_image_id(monkeypatch):
    gallery = import_gallery(monkeypatch)
    images = [
        {"id": 10, "groupId": None},
        {"id": 10, "groupId": None, "title": "same post"},
        {"id": 11},
    ]

    posts = gallery.group_images_into_posts(images)

    assert posts == [
        [{"id": 10, "groupId": None}, {"id": 10, "groupId": None, "title": "same post"}],
        [{"id": 11}],
    ]


def test_group_images_into_posts_returns_empty_list_for_empty_input(monkeypatch):
    gallery = import_gallery(monkeypatch)

    assert gallery.group_images_into_posts([]) == []
