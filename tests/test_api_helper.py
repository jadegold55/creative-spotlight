import asyncio
import importlib
import sys


def import_api(monkeypatch):
    monkeypatch.setenv("API_SERVICE_TOKEN", "test-token")
    monkeypatch.setenv("BACKEND_URL", "http://backend.test")
    monkeypatch.setenv("PUBLIC_URL", "http://public.test")
    sys.modules.pop("bot.apihelper.api", None)
    sys.modules.pop("bot.config", None)
    return importlib.import_module("bot.apihelper.api")


class FakeResponse:
    def __init__(self, status=200, payload=None, text=""):
        self.status = status
        self.payload = payload if payload is not None else {}
        self.text_value = text

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def json(self):
        return self.payload

    async def text(self):
        return self.text_value


class FakeSession:
    def __init__(self, responses=None, headers=None):
        self.responses = list(responses or [])
        self.headers = headers
        self.calls = []
        self.closed = False

    def _response(self):
        return self.responses.pop(0)

    def get(self, url, params=None, headers=None):
        self.calls.append(("GET", url, params, headers))
        return self._response()

    def post(self, url, params=None, data=None, headers=None):
        self.calls.append(("POST", url, params, data, headers))
        return self._response()

    def delete(self, url, params=None, headers=None):
        self.calls.append(("DELETE", url, params, headers))
        return self._response()

    async def close(self):
        self.closed = True


def test_get_session_creates_authorized_reusable_session(monkeypatch):
    api = import_api(monkeypatch)
    created_sessions = []

    def client_session(headers=None):
        session = FakeSession(headers=headers)
        created_sessions.append(session)
        return session

    monkeypatch.setattr(api.aiohttp, "ClientSession", client_session)

    first = asyncio.run(api._get_session())
    second = asyncio.run(api._get_session())

    assert first is second
    assert created_sessions == [first]
    assert first.headers == {"Authorization": "Bearer test-token"}


def test_get_returns_json_for_success_and_normalizes_path(monkeypatch):
    api = import_api(monkeypatch)
    session = FakeSession([FakeResponse(payload={"ok": True})])
    api._session = session

    result = asyncio.run(
        api.get(
            "/images/all",
            params={"guildId": 42},
            headers={"X-Command": "gallery"},
        )
    )

    assert result == {"ok": True}
    assert session.calls == [
        (
            "GET",
            "http://backend.test/images/all",
            {"guildId": 42},
            {"X-Command": "gallery"},
        )
    ]


def test_get_returns_none_for_non_200(monkeypatch):
    api = import_api(monkeypatch)
    api._session = FakeSession([FakeResponse(status=404, payload={"error": "missing"})])

    result = asyncio.run(api.get("images/99"))

    assert result is None


def test_post_and_delete_return_status_and_text(monkeypatch):
    api = import_api(monkeypatch)
    session = FakeSession(
        [
            FakeResponse(status=201, text="created"),
            FakeResponse(status=204, text=""),
        ]
    )
    api._session = session

    post_result = asyncio.run(api.post("images/add", data="form"))
    delete_result = asyncio.run(api.delete("/images/1"))

    assert post_result == (201, "created")
    assert delete_result == (204, "")
    assert session.calls[0] == (
        "POST",
        "http://backend.test/images/add",
        None,
        "form",
        None,
    )
    assert session.calls[1] == (
        "DELETE",
        "http://backend.test/images/1",
        None,
        None,
    )


def test_close_session_closes_and_clears_shared_session(monkeypatch):
    api = import_api(monkeypatch)
    session = FakeSession()
    api._session = session

    asyncio.run(api.close_session())

    assert session.closed is True
    assert api._session is None
