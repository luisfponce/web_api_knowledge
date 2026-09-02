import asyncio
import logging

from infrastructure.notifications import scheduler, slack_service


def test_send_slack_notification_disabled_makes_no_http_call(monkeypatch):
    calls = []

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            calls.append((args, kwargs))

    monkeypatch.setattr(slack_service, "_is_pytest_running", lambda: False)
    monkeypatch.setattr(slack_service.config, "SLACK_NOTIFICATIONS_ENABLED", False)
    monkeypatch.setattr(slack_service.config, "SLACK_WEBHOOK_URL", "https://hooks.slack.test/example")
    monkeypatch.setattr(slack_service.httpx, "AsyncClient", FakeAsyncClient)

    asyncio.run(slack_service.send_slack_notification("ignored"))

    assert calls == []


def test_send_slack_notification_missing_url_makes_no_http_call(monkeypatch):
    calls = []

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            calls.append((args, kwargs))

    monkeypatch.setattr(slack_service, "_is_pytest_running", lambda: False)
    monkeypatch.setattr(slack_service.config, "SLACK_NOTIFICATIONS_ENABLED", True)
    monkeypatch.setattr(slack_service.config, "SLACK_WEBHOOK_URL", "")
    monkeypatch.setattr(slack_service.httpx, "AsyncClient", FakeAsyncClient)

    asyncio.run(slack_service.send_slack_notification("ignored"))

    assert calls == []


def test_send_slack_notification_under_pytest_makes_no_http_call(monkeypatch):
    calls = []

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            calls.append((args, kwargs))

    monkeypatch.setattr(slack_service.config, "SLACK_NOTIFICATIONS_ENABLED", True)
    monkeypatch.setattr(slack_service.config, "SLACK_WEBHOOK_URL", "https://hooks.slack.test/example")
    monkeypatch.setattr(slack_service.httpx, "AsyncClient", FakeAsyncClient)

    asyncio.run(slack_service.send_slack_notification("ignored"))

    assert calls == []


def test_send_slack_notification_posts_expected_json(monkeypatch):
    calls = []

    class FakeResponse:
        def raise_for_status(self):
            calls.append(("raise_for_status",))

    class FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return None

        async def post(self, url, json):
            calls.append((url, json, self.timeout))
            return FakeResponse()

    monkeypatch.setattr(slack_service, "_is_pytest_running", lambda: False)
    monkeypatch.setattr(slack_service.config, "SLACK_NOTIFICATIONS_ENABLED", True)
    monkeypatch.setattr(slack_service.config, "SLACK_WEBHOOK_URL", "https://hooks.slack.test/example")
    monkeypatch.setattr(slack_service.config, "SLACK_NOTIFICATION_TIMEOUT_SECONDS", 2.5)
    monkeypatch.setattr(slack_service.httpx, "AsyncClient", FakeAsyncClient)

    asyncio.run(slack_service.send_slack_notification("hello", blocks=[{"type": "section"}]))

    assert calls == [
        (
            "https://hooks.slack.test/example",
            {"text": "hello", "blocks": [{"type": "section"}]},
            2.5,
        ),
        ("raise_for_status",),
    ]


def test_notification_background_wrapper_logs_and_swallows_errors(caplog):
    async def failing_notification():
        raise Exception("slack unavailable")

    with caplog.at_level(logging.ERROR, logger="infrastructure.notifications.scheduler"):
        asyncio.run(scheduler._run_notification(lambda: failing_notification()))

    assert "Notification delivery failed" in caplog.text
