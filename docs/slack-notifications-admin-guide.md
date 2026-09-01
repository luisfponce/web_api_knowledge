# Slack Notifications Setup Guide

This guide explains how to connect this project to Slack so administrators can receive quick notifications when important activity happens.

## What This Does

When Slack notifications are turned on, the system sends a message to one Slack channel when:

- A new user account is created.
- A logged-in user creates a new prompt.

The system does not send Slack messages for the three default prompts that are automatically created during signup.

Slack phone alerts are handled by the Slack mobile app. If the message appears in Slack but not on a phone, check the Slack mobile notification settings for the user and channel.

## Before You Start

You need:

- Administrator access to the Slack workspace that should receive the notifications.
- Permission in Slack to create apps or manage Incoming Webhooks.
- Access to the project configuration, such as the local `.env` file, deployment environment variables, or hosting provider settings.
- Permission to restart or redeploy the backend after changing the settings.

## Step 1: Create A Slack Webhook

1. Open `https://api.slack.com/apps` in your browser.
2. Select `Create New App`.
3. Choose `From scratch`.
4. Enter an app name, for example `WebAPI Notifications`.
5. Select the Slack workspace that should receive the messages.
6. Open `Incoming Webhooks` in the Slack app settings.
7. Turn on `Activate Incoming Webhooks`.
8. Select `Add New Webhook to Workspace`.
9. Choose the Slack channel where notifications should appear.
10. Approve the Slack permission request.
11. Copy the webhook URL that Slack creates.

The webhook URL usually starts with `https://hooks.slack.com/services/`.

Treat this URL like a password. Anyone who has it may be able to send messages to the selected Slack channel.

## Step 2: Add Slack Settings To The Project

The project uses three Slack settings:

- `SLACK_NOTIFICATIONS_ENABLED`: turns Slack notifications on or off.
- `SLACK_WEBHOOK_URL`: tells the backend which Slack channel webhook to use.
- `SLACK_NOTIFICATION_TIMEOUT_SECONDS`: controls how long the backend waits for Slack before giving up. The normal value is `5`.

For local Docker Compose or local Python runs, open the root `.env` file. If it does not exist yet, create it from the template:

```bash
cp .env.example .env
```

Add or update these lines in `.env`:

```env
SLACK_NOTIFICATIONS_ENABLED=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/REPLACE/THIS/VALUE
SLACK_NOTIFICATION_TIMEOUT_SECONDS=5
```

Replace `https://hooks.slack.com/services/REPLACE/THIS/VALUE` with the webhook URL copied from Slack.

For production or another hosted environment, add the same three settings in the place where that environment stores secrets or environment variables. This may be a deployment platform, server control panel, CI/CD secret manager, or hosting provider dashboard.

Do not put a real Slack webhook URL in Git, screenshots, public tickets, or shared documents.

## Step 3: Restart Or Redeploy The Backend

The backend reads these settings when it starts. After changing Slack settings, restart or redeploy the backend.

For Docker Compose, restart from the repository root:

```bash
docker compose up --build -d
```

If your machine uses the older Compose command, use:

```bash
docker-compose up --build -d
```

For a hosted environment, use the normal deploy or restart process for that environment.

## Step 4: Send A Test Notification

To confirm everything works:

1. Create a test user through the app or through `POST /api/v1/auth/signup`.
2. Confirm one Slack message appears with the title `New user registered`.
3. Log in as that user.
4. Create one prompt through the app or through `POST /api/v1/prompts`.
5. Confirm one Slack message appears with the title `New prompt added`.
6. Confirm signup did not create three extra Slack messages for the default prompts.

## What Messages Look Like

New user notifications look like this:

```text
New user registered
ID: 123
Username: jane
Email: jane@example.com
Language: en
Role: user
```

New prompt notifications look like this:

```text
New prompt added
Prompt ID: 456
Owner: jane (123)
Title: My research assistant
Model: gpt
Category: research
Rate: 5
```

Prompt messages do not include the full prompt text. This keeps Slack messages short and avoids exposing large prompt content in the notification channel.

## Troubleshooting

If no Slack message appears, confirm `SLACK_NOTIFICATIONS_ENABLED=true`.

If no Slack message appears, confirm `SLACK_WEBHOOK_URL` starts with `https://hooks.slack.com/services/` and was copied completely.

If no Slack message appears after editing `.env`, restart or redeploy the backend.

If messages appear locally but not in production, confirm the production environment has the Slack settings. Local `.env` values do not automatically configure production.

If messages go to the wrong Slack channel, create a new webhook for the correct channel and replace `SLACK_WEBHOOK_URL` with the new URL.

If Slack messages appear but phone alerts do not, check the Slack mobile app, channel mute settings, workspace notification settings, and phone notification permissions.

If Slack is temporarily unavailable, users and prompts should still be saved. Slack delivery is best-effort and should not block normal app activity.

## Security Tips

Keep the webhook URL private.

Do not commit the real webhook URL to Git.

Do not paste the real webhook URL into public chat, tickets, screenshots, or documentation.

If the webhook URL is exposed, revoke it in Slack and create a new webhook.

Use a dedicated Slack channel when possible, so notification access is easy to manage.
