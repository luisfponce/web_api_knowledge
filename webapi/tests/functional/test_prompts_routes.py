import api.endpoints.v1.prompts as prompts_module
from auth.auth_service import crear_jwt
from models.prompts import Prompts
from models.user import User


def auth_headers_for(user: User) -> dict[str, str]:
    token = crear_jwt({"sub": user.username, "role": user.role, "user_id": user.id})
    return {"Authorization": f"Bearer {token}"}


def create_user(db_session, username: str, role: str = "user") -> User:
    user = User(
        username=username,
        name=username,
        last_name="User",
        phone=5500001000 + len(username),
        email=f"{username}@example.com",
        hashed_password="password",
        role=role,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_prompt(db_session, user_id: int, category: str = "qa", model_name: str = "gpt-4.1", rate: int = 5) -> Prompts:
    prompt = Prompts(
        user_id=user_id,
        model_name=model_name,
        prompt_text=f"{category} prompt {rate}",
        category=category,
        rate=rate,
    )
    db_session.add(prompt)
    db_session.commit()
    db_session.refresh(prompt)
    return prompt


def test_create_prompt_success(client, auth_header, created_user):
    payload = {
        "user_id": created_user.id,
        "model_name": "gpt-4.1",
        "prompt_text": "Generate answer",
        "category": "qa",
        "rate": 5,
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
        "rate": 5,
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
        "rate": 5,
    }

    response = client.post("/api/v1/prompts", json=payload, headers=auth_header)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_regular_user_cannot_create_prompt_for_another_user(client, auth_header, db_session):
    other_user = create_user(db_session, "create_other_user")
    payload = {
        "user_id": other_user.id,
        "model_name": "gpt-4.1",
        "prompt_text": "not allowed",
        "category": "qa",
        "rate": 5,
    }

    response = client.post("/api/v1/prompts", json=payload, headers=auth_header)

    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot create prompts for another user"


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
        "rate": 3,
    }
    headers = {**auth_header, "send_email": "true"}

    response = client.post("/api/v1/prompts", json=payload, headers=headers)

    assert response.status_code == 200
    assert called["value"] is True


def test_create_prompt_send_email_exception_still_success(client, auth_header, created_user, monkeypatch):
    async def failing_send_email(*args, **kwargs):
        raise Exception("smtp unavailable")

    monkeypatch.setattr(prompts_module, "send_email", failing_send_email)

    payload = {
        "user_id": created_user.id,
        "model_name": "gpt-4.1",
        "prompt_text": "Ignore email failure",
        "category": "ops",
        "rate": 1,
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


def test_admin_can_filter_prompts(client, db_session, created_prompt):
    owner = db_session.get(User, created_prompt.user_id)
    admin = create_user(db_session, "filter_admin", role="admin")
    create_prompt(db_session, owner.id, category="dev", model_name="gpt-4o-mini", rate=3)
    create_prompt(db_session, admin.id, category="qa", model_name="gpt-4.1", rate=5)

    response = client.get(
        "/api/v1/prompts",
        params={"user_id": owner.id, "category": "dev", "model_name": "gpt-4o-mini", "rate": 3},
        headers=auth_headers_for(admin),
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["user_id"] == owner.id
    assert response.json()[0]["category"] == "dev"
    assert response.json()[0]["model_name"] == "gpt-4o-mini"
    assert response.json()[0]["rate"] == 3


def test_read_prompts_pagination(client, db_session, created_user, auth_header):
    first_prompt = create_prompt(db_session, created_user.id, category="qa", rate=1)
    second_prompt = create_prompt(db_session, created_user.id, category="dev", rate=2)

    response = client.get("/api/v1/prompts", params={"skip": 1, "limit": 1}, headers=auth_header)

    assert response.status_code == 200
    assert len(response.json()) == 1
    returned_id = response.json()[0]["id"]
    assert returned_id in {first_prompt.id, second_prompt.id}
    assert returned_id != min(first_prompt.id, second_prompt.id)


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
        "rate": 3,
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
        "rate": 5,
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
        "rate": 5,
    }

    response = client.put(f"/api/v1/prompts/{created_prompt.id}", json=payload, headers=auth_header)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found for this prompt"


def test_god_can_update_another_users_prompt(client, db_session, created_prompt):
    god = create_user(db_session, "update_god", role="god")
    payload = {
        "user_id": created_prompt.user_id,
        "model_name": "gpt-5",
        "prompt_text": "god update",
        "category": "research",
        "rate": 4,
    }

    response = client.put(
        f"/api/v1/prompts/{created_prompt.id}",
        json=payload,
        headers=auth_headers_for(god),
    )

    assert response.status_code == 200
    assert response.json()["model_name"] == "gpt-5"
    assert response.json()["prompt_text"] == "god update"


def test_prompt_rating_validation_rejects_out_of_range_values(client, auth_header, created_user):
    payload = {
        "user_id": created_user.id,
        "model_name": "gpt-4.1",
        "prompt_text": "bad rating",
        "category": "qa",
        "rate": 6,
    }

    response = client.post("/api/v1/prompts", json=payload, headers=auth_header)

    assert response.status_code == 422


def test_prompt_rating_validation_rejects_non_integer_values(client, auth_header, created_user):
    payload = {
        "user_id": created_user.id,
        "model_name": "gpt-4.1",
        "prompt_text": "bad rating",
        "category": "qa",
        "rate": 3.5,
    }

    response = client.post("/api/v1/prompts", json=payload, headers=auth_header)

    assert response.status_code == 422


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


def test_admin_cannot_delete_prompt(client, db_session, created_prompt):
    admin = create_user(db_session, "delete_admin", role="admin")

    response = client.delete(
        f"/api/v1/prompts/{created_prompt.id}",
        headers=auth_headers_for(admin),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admins cannot delete prompts"


def test_regular_user_cannot_read_another_users_prompt(client, auth_header, db_session):
    other_user = User(
        username="other_prompt_user",
        name="Other",
        last_name="User",
        phone=5500000190,
        email="other_prompt_user@example.com",
        hashed_password="password",
    )
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(other_user)
    prompt = Prompts(
        user_id=other_user.id,
        model_name="gpt-4.1",
        prompt_text="private prompt",
        category="qa",
        rate=4,
    )
    db_session.add(prompt)
    db_session.commit()
    db_session.refresh(prompt)

    response = client.get(f"/api/v1/prompts/{prompt.id}", headers=auth_header)

    assert response.status_code == 403


def test_admin_can_read_all_prompts_but_cannot_update(client, db_session, created_prompt):
    admin = User(
        username="admin_user",
        name="Admin",
        last_name="User",
        phone=5500000191,
        email="admin_user@example.com",
        hashed_password="password",
        role="admin",
    )
    db_session.add(admin)
    db_session.commit()
    token = crear_jwt({"sub": admin.username, "role": "admin", "user_id": admin.id})
    headers = {"Authorization": f"Bearer {token}"}

    read_response = client.get("/api/v1/prompts", headers=headers)

    assert read_response.status_code == 200
    assert read_response.json()[0]["id"] == created_prompt.id

    update_response = client.put(
        f"/api/v1/prompts/{created_prompt.id}",
        json={
            "user_id": created_prompt.user_id,
            "model_name": "gpt-4o-mini",
            "prompt_text": "admin update",
            "category": "dev",
            "rate": 3,
        },
        headers=headers,
    )

    assert update_response.status_code == 403


def test_god_can_delete_another_users_prompt(client, db_session, created_prompt):
    god = User(
        username="god_user",
        name="God",
        last_name="User",
        phone=5500000192,
        email="god_user@example.com",
        hashed_password="password",
        role="god",
    )
    db_session.add(god)
    db_session.commit()
    token = crear_jwt({"sub": god.username, "role": "god", "user_id": god.id})

    response = client.delete(
        f"/api/v1/prompts/{created_prompt.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == created_prompt.id
