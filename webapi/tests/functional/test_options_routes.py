from api.endpoints.v1.options import CATEGORY_OPTIONS, MODEL_OPTIONS


def test_read_category_options(client, auth_header):
    response = client.get("/api/v1/options/categories", headers=auth_header)

    assert response.status_code == 200
    assert response.json()["items"][0] == {"value": "qa", "label": "QA"}


def test_read_model_options(client, auth_header):
    response = client.get("/api/v1/options/models", headers=auth_header)

    assert response.status_code == 200
    assert response.json()["items"][0] == {"value": "gpt-4.1", "label": "GPT-4.1"}


def test_read_category_options_unauthorized(client):
    response = client.get("/api/v1/options/categories", headers={"Authorization": "Bearer invalid"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized token"


def test_read_model_options_unauthorized(client):
    response = client.get("/api/v1/options/models", headers={"Authorization": "Bearer invalid"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized token"


def test_option_items_have_stable_shape(client, auth_header):
    for path in ("/api/v1/options/categories", "/api/v1/options/models"):
        response = client.get(path, headers=auth_header)

        assert response.status_code == 200
        assert response.json()["items"]
        for item in response.json()["items"]:
            assert set(item) == {"value", "label"}
            assert isinstance(item["value"], str)
            assert isinstance(item["label"], str)


def test_prompt_options_align_with_known_backend_values(client, auth_header):
    category_response = client.get("/api/v1/options/categories", headers=auth_header)
    model_response = client.get("/api/v1/options/models", headers=auth_header)

    assert category_response.status_code == 200
    assert model_response.status_code == 200
    assert {item["value"] for item in category_response.json()["items"]} == {
        item["value"] for item in CATEGORY_OPTIONS
    }
    assert {item["value"] for item in model_response.json()["items"]} == {
        item["value"] for item in MODEL_OPTIONS
    }
