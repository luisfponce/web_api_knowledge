import logging
from collections.abc import Awaitable, Callable

from fastapi import BackgroundTasks

logger = logging.getLogger(__name__)


async def _run_notification(coro_factory: Callable[[], Awaitable[None]]) -> None:
    try:
        await coro_factory()
    except Exception:
        logger.exception("Notification delivery failed")


def schedule_notification(
    background_tasks: BackgroundTasks,
    coro_factory: Callable[[], Awaitable[None]],
) -> None:
    background_tasks.add_task(_run_notification, coro_factory)
