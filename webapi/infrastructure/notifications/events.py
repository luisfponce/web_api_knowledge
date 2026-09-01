from models.prompts import Prompts
from models.user import User
from infrastructure.notifications.slack_service import send_slack_notification


async def notify_user_created(user: User) -> None:
    text = (
        "New user registered\n"
        f"ID: {user.id}\n"
        f"Username: {user.username}\n"
        f"Email: {user.email}\n"
        f"Language: {user.preferred_language}\n"
        f"Role: {user.role}"
    )
    await send_slack_notification(text)


async def notify_prompt_created(prompt: Prompts, user: User) -> None:
    text = (
        "New prompt added\n"
        f"Prompt ID: {prompt.id}\n"
        f"Owner: {user.username} ({user.id})\n"
        f"Title: {prompt.title}\n"
        f"Model: {prompt.model_name}\n"
        f"Category: {prompt.category}\n"
        f"Rate: {prompt.rate}"
    )
    await send_slack_notification(text)
