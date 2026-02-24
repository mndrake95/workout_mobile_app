import pytest
from helpers import register_and_login_scenario

# Создание упражнения

@pytest.mark.anyio
async def test_create_exercise_authorized(client):
    create_data, login_data = await register_and_login_scenario(client, username="test_user", email="test@example.com")
    response = await client.post("/exercises", 
                                 headers={"Authorization": f"Bearer {login_data['access_token']}"},
                                 json={"title": "test_title",
                                         "type": "test_type",
                                         "body_parts": "test_body_parts"})
    data = response.json()

    assert "id" in data
    assert isinstance(data["id"], int)
    assert data["title"] == "test_title"
    assert data["type"] == "test_type"
    assert data["body_parts"] == "test_body_parts"
    assert data["author"] == create_data["id"]
    assert response.status_code == 201

@pytest.mark.anyio
async def test_create_exercise_unauthorized(client):
    response = await client.post("/exercises", 
                             headers={"Authorization": f"Bearer"},
                             json={"title": "test_title",
                                     "type": "test_type",
                                     "body_parts": "test_body_parts"})

    assert response.status_code == 401

# Получение списка упражнений

@pytest.mark.anyio
async def test_get_list_of_exercises_no_auth_needed(client):
    _, login_data = await register_and_login_scenario(client, username="test_user", email="test@example.com")
    post1 = await client.post("/exercises", 
                             headers={"Authorization": f"Bearer {login_data['access_token']}"},
                             json={"title": "test_title1",
                                     "type": "test_type1",
                                     "body_parts": "test_body_parts1"})
    post2 = await client.post("/exercises", 
                             headers={"Authorization": f"Bearer {login_data['access_token']}"},
                             json={"title": "test_title2",
                                     "type": "test_type2",
                                     "body_parts": "test_body_parts2"})
    response = await client.get("/exercises")
    
    data = response.json()

    assert len(data["items"]) == 2
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["pages"] == 1
