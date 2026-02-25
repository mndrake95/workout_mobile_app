import pytest
from .helpers import register_and_login_scenario

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

    assert all(item["is_mine"] == False for item in data["items"])
    assert len(data["items"]) == 2
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["pages"] == 1

@pytest.mark.anyio
async def test_get_list_of_exercises_with_filter(client):
    _, login_data = await register_and_login_scenario(client, username="test_user", email="test@example.com")
    post1 = await client.post("/exercises", 
                             headers={"Authorization": f"Bearer {login_data['access_token']}"},
                             json={"title": "test_title1",
                                     "type": "test_type12",
                                     "body_parts": "test_body_parts1"})
    post2 = await client.post("/exercises", 
                             headers={"Authorization": f"Bearer {login_data['access_token']}"},
                             json={"title": "test_title2",
                                     "type": "test_type2",
                                     "body_parts": "test_body_parts12"})
    response = await client.get("/exercises", params={"type": "test_type12"})
    data = response.json()
    
    assert len(data["items"]) == 1
    assert data["total"] == 1

@pytest.mark.anyio
async def test_get_exercise_by_id(client):
    _, login_data = await register_and_login_scenario(client, username="test_user", email="test@example.com")
    post1 = await client.post("/exercises", 
                             headers={"Authorization": f"Bearer {login_data['access_token']}"},
                             json={"title": "test_title1",
                                     "type": "test_type12",
                                     "body_parts": "test_body_parts1"})
    post1_data = post1.json()
    response = await client.get(f"/exercises/{post1_data['id']}")
    data = response.json()

    assert data["id"] == post1_data["id"]
    assert data["title"] == post1_data["title"]
    assert data["type"] == post1_data["type"]
    assert data["body_parts"] == post1_data["body_parts"]

@pytest.mark.anyio
async def test_get_exercise_by_id_not_found(client):
    response = await client.get("/exercises/99999999")
    
    assert response.status_code == 404

@pytest.mark.anyio
async def test_get_exercise_list_own_exercises(client):
    create_data, login_data = await register_and_login_scenario(client, username="test_user", email="test@example.com")
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
    response = await client.get("/exercises",
                                headers={"Authorization": f"Bearer {login_data['access_token']}"},
                                )
    
    data = response.json()

    assert all(item["is_mine"] == True for item in data["items"])

@pytest.mark.anyio
async def test_get_exercise_list_others(client):
    create_data1, login_data1 = await register_and_login_scenario(client, username="test_user1", email="test@example1.com")
    create_data2, login_data2 = await register_and_login_scenario(client, username="test_user2", email="test@example2.com")
    post1 = await client.post("/exercises", 
                             headers={"Authorization": f"Bearer {login_data1['access_token']}"},
                             json={"title": "test_title1",
                                     "type": "test_type1",
                                     "body_parts": "test_body_parts1"})
    post2 = await client.post("/exercises", 
                             headers={"Authorization": f"Bearer {login_data1['access_token']}"},
                             json={"title": "test_title2",
                                     "type": "test_type2",
                                     "body_parts": "test_body_parts2"})
    response = await client.get("/exercises",
                                headers={"Authorization": f"Bearer {login_data2['access_token']}"},
                                )
    
    data = response.json()

    assert all(item["is_mine"] == False for item in data["items"])

# Обновление упражнения 

@pytest.mark.anyio
async def test_patch_exercise_as_author(client):
    _, login_data = await register_and_login_scenario(client, username="test_user", email="test@example.com")
    response = await client.post("/exercises", 
                                 headers={"Authorization": f"Bearer {login_data['access_token']}"},
                                 json={"title": "test_title",
                                         "type": "test_type",
                                         "body_parts": "test_body_parts"})
    response_data = response.json()
    update = await client.patch(f"/exercises/{response_data['id']}",
                                 headers={"Authorization": f"Bearer {login_data['access_token']}"},
                                 json={"title": "patch_test_title"}
                                 )
    update_data = update.json()

    assert update_data["title"] == "patch_test_title"
    assert update.status_code == 200

@pytest.mark.anyio
async def test_patch_exercise_as_non_author(client):
    _, login_data1 = await register_and_login_scenario(client, username="test_user1", email="test@example1.com")
    _, login_data2 = await register_and_login_scenario(client, username="test_user2", email="test@example2.com")
    response = await client.post("/exercises", 
                                 headers={"Authorization": f"Bearer {login_data1['access_token']}"},
                                 json={"title": "test_title",
                                         "type": "test_type",
                                         "body_parts": "test_body_parts"})
    response_data = response.json()
    update = await client.patch(f"/exercises/{response_data['id']}",
                                 headers={"Authorization": f"Bearer {login_data2['access_token']}"},
                                 json={"title": "patch_test_title"}
                                 )

    assert update.status_code == 403

@pytest.mark.anyio
async def test_patch_exercise_unauthenticated(client):
    _, login_data = await register_and_login_scenario(client, username="test_user", email="test@example.com")
    response = await client.post("/exercises", 
                                 headers={"Authorization": f"Bearer {login_data['access_token']}"},
                                 json={"title": "test_title",
                                         "type": "test_type",
                                         "body_parts": "test_body_parts"})
    response_data = response.json()
    update = await client.patch(f"/exercises/{response_data['id']}",
                                 headers={"Authorization": f"Bearer "},
                                 json={"title": "patch_test_title"}
                                 )

    assert update.status_code == 401

@pytest.mark.anyio
async def test_patch_exercise_not_found(client):
    _, login_data = await register_and_login_scenario(client, username="test_user", email="test@example.com")
    update = await client.patch(f"/exercises/9999999",
                                 headers={"Authorization": f"Bearer {login_data['access_token']}"},
                                 json={"title": "patch_test_title"}
                                 )
    
    assert update.status_code == 404

# Удаление упражнений

@pytest.mark.anyio
async def test_delete_exercise_as_author(client):
    _, login_data = await register_and_login_scenario(client, username="test_user", email="test@example.com")
    response = await client.post("/exercises", 
                                 headers={"Authorization": f"Bearer {login_data['access_token']}"},
                                 json={"title": "test_title",
                                         "type": "test_type",
                                         "body_parts": "test_body_parts"})
    response_data = response.json()
    delete = await client.delete(f"/exercises/{response_data['id']}",
                                 headers={"Authorization": f"Bearer {login_data['access_token']}"},
                                 )

    assert delete.status_code == 204

@pytest.mark.anyio
async def test_delete_exercise_as_non_author(client):
    _, login_data1 = await register_and_login_scenario(client, username="test_user1", email="test@example1.com")
    _, login_data2 = await register_and_login_scenario(client, username="test_user2", email="test@example2.com")
    response = await client.post("/exercises", 
                                 headers={"Authorization": f"Bearer {login_data1['access_token']}"},
                                 json={"title": "test_title",
                                         "type": "test_type",
                                         "body_parts": "test_body_parts"})
    response_data = response.json()
    delete = await client.delete(f"/exercises/{response_data['id']}",
                                 headers={"Authorization": f"Bearer {login_data2['access_token']}"},
                                 )

    assert delete.status_code == 403

@pytest.mark.anyio
async def test_delete_exercise_unauthenticated(client):
    _, login_data = await register_and_login_scenario(client, username="test_user", email="test@example.com")
    response = await client.post("/exercises", 
                                 headers={"Authorization": f"Bearer {login_data['access_token']}"},
                                 json={"title": "test_title",
                                         "type": "test_type",
                                         "body_parts": "test_body_parts"})
    response_data = response.json()
    delete = await client.delete(f"/exercises/{response_data['id']}",
                                 headers={"Authorization": f"Bearer "},
                                 )

    assert delete.status_code == 401
