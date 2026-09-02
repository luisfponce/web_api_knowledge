import os
import sys

import httpx

from core import config


def _is_pytest_running() -> bool:
    return "PYTEST_CURRENT_TEST" in os.environ or "pytest" in sys.modules


async def send_slack_notification(text: str, blocks: list[dict] | None = None) -> None:
    if (
        _is_pytest_running()
        or not config.SLACK_NOTIFICATIONS_ENABLED
        or not config.SLACK_WEBHOOK_URL
    ):
        return

    payload: dict[str, object] = {"text": text}
    if blocks is not None:
        payload["blocks"] = blocks

    async with httpx.AsyncClient(timeout=config.SLACK_NOTIFICATION_TIMEOUT_SECONDS) as client:
        response = await client.post(config.SLACK_WEBHOOK_URL, json=payload)
        response.raise_for_status()
