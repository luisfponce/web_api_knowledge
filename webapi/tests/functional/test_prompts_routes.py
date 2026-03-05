import api.endpoints.v1.prompts as prompts_module


def test_create_prompt_success(client, auth_header, created_user):
    payload = {
        "user_id": created_user.id,
        "model_name": "gpt-4.1",
        "prompt_text": "Generate answer",
        "category": "qa",
        "rate": "high",
    }

    response = client.post("/api/v1/prompts", json=payload, headers=auth_header)

    assert response.status_code == 200
    assert response.json()["user_id"] == created_user.id
    assert response.json()["model_name"] == "gpt-4.1"


def test_create_prompt_unauthorized_returns_401(client, created_user):
    payload = {
        "user_id": created_user.id,
        "model_name": "gpt-4.1",
        "prompt_text": "Generate answer",
        "category": "qa",
        "rate": "high",
    }

    response = client.post(
        "/api/v1/prompts",
        json=payload,
        headers={"Authorization": "Bearer invalid"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized token"


def test_create_prompt_user_not_found_returns_404(client, auth_header):
    payload = {
        "user_id": 9999,
        "model_name": "gpt-4.1",
        "prompt_text": "Generate answer",
        "category": "qa",
        "rate": "high",
    }

    response = client.post("/api/v1/prompts", json=payload, headers=auth_header)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_create_prompt_send_email_true_calls_email(client, auth_header, created_user, monkeypatch):
    called = {"value": False}

    async def fake_send_email(to, username, message_body=""):
        called["value"] = True
        assert to == created_user.email
        assert username == created_user.username

    monkeypatch.setattr(prompts_module, "send_email", fake_send_email)

    payload = {
        "user_id": created_user.id,
        "model_name": "gpt-4.1",
        "prompt_text": "Notify me",
        "category": "qa",
        "rate": "medium",
    }
    headers = {**auth_header, "send_email": "true"}

    response = client.post("/api/v1/prompts", json=payload, headers=headers)

    assert response.status_code == 200
    assert called["value"] is True


def test_create_prompt_send_email_exception_still_success(
    client, auth_header, created_user, monkeypatch
):
    async def failing_send_email(*args, **kwargs):
        raise Exception("smtp unavailable")

    monkeypatch.setattr(prompts_module, "send_email", failing_send_email)

    payload = {
        "user_id": created_user.id,
        "model_name": "gpt-4.1",
        "prompt_text": "Ignore email failure",
        "category": "ops",
        "rate": "low",
    }
    headers = {**auth_header, "send_email": "true"}

    response = client.post("/api/v1/prompts", json=payload, headers=headers)

    assert response.status_code == 200
    assert response.json()["prompt_text"] == "Ignore email failure"


def test_read_prompts_success(client, auth_header, created_prompt):
    response = client.get("/api/v1/prompts", headers=auth_header)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == created_prompt.id


def test_read_prompts_empty_returns_404(client, auth_header):
    response = client.get("/api/v1/prompts", headers=auth_header)

    assert response.status_code == 404
    assert response.json()["detail"] == "No prompts found"


def test_read_prompts_unauthorized_returns_401(client):
    response = client.get("/api/v1/prompts", headers={"Authorization": "Bearer invalid"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized token"


def test_get_prompt_success(client, auth_header, created_prompt):
    response = client.get(f"/api/v1/prompts/{created_prompt.id}", headers=auth_header)

    assert response.status_code == 200
    assert response.json()["id"] == created_prompt.id


def test_get_prompt_missing_returns_404(client, auth_header):
    response = client.get("/api/v1/prompts/9999", headers=auth_header)

    assert response.status_code == 404
    assert response.json()["detail"] == "Prompt not found"


def test_update_prompt_success(client, auth_header, created_prompt, created_user):
    payload = {
        "user_id": created_user.id,
        "model_name": "gpt-4o-mini",
        "prompt_text": "Updated prompt",
        "category": "dev",
        "rate": "medium",
    }

    response = client.put(f"/api/v1/prompts/{created_prompt.id}", json=payload, headers=auth_header)

    assert response.status_code == 200
    assert response.json()["model_name"] == "gpt-4o-mini"
    assert response.json()["prompt_text"] == "Updated prompt"


def test_update_prompt_missing_returns_404(client, auth_header, created_user):
    payload = {
        "user_id": created_user.id,
        "model_name": "gpt-4.1",
        "prompt_text": "Updated prompt",
        "category": "qa",
        "rate": "high",
    }

    response = client.put("/api/v1/prompts/9999", json=payload, headers=auth_header)

    assert response.status_code == 404
    assert response.json()["detail"] == "Prompt not found"


def test_update_prompt_user_not_found_returns_404(client, auth_header, created_prompt):
    payload = {
        "user_id": 9999,
        "model_name": "gpt-4.1",
        "prompt_text": "Updated prompt",
        "category": "qa",
        "rate": "high",
    }

    response = client.put(f"/api/v1/prompts/{created_prompt.id}", json=payload, headers=auth_header)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found for this prompt"


def test_delete_prompt_success(client, auth_header, created_prompt):
    response = client.delete(f"/api/v1/prompts/{created_prompt.id}", headers=auth_header)

    assert response.status_code == 200
    assert response.json()["id"] == created_prompt.id


def test_delete_prompt_missing_returns_404(client, auth_header):
    response = client.delete("/api/v1/prompts/9999", headers=auth_header)

    assert response.status_code == 404
    assert response.json()["detail"] == "Prompt not found to delete"


def test_delete_prompt_unauthorized_returns_401(client):
    response = client.delete("/api/v1/prompts/1", headers={"Authorization": "Bearer invalid"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized token"
