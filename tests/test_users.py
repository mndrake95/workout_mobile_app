import pytest

# Регистрация пользователя

@pytest.mark.anyio
async def test_register_user(client):
    response = await client.post("/users/register", json={"username": "test_user", 
                                                          "email": "test@example.com", 
                                                          "password": "test_password"})
    data = response.json()
    
    assert "id" in data
    assert isinstance(data["id"], int)
    assert data["username"] == "test_user"
    assert data["email"] == "test@example.com"
    assert "password" not in data
    assert response.status_code == 201

# Сценарии логина пользователя

@pytest.mark.anyio
async def test_login_with_username_only(client):
    create = await client.post("/users/register", json={"username": "test_user", 
                                                          "email": "test@example.com", 
                                                          "password": "test_password"})
    create_data = create.json()

    login = await client.post("/users/login", json={"username": create_data["username"],
                                                    "password": "test_password"})
    login_data = login.json()
    assert "access_token" in login_data
    assert isinstance(login_data["access_token"], str)
    assert len(login_data["access_token"]) > 0
    assert login.status_code == 200

@pytest.mark.anyio
async def test_login_with_email_only(client):
    create = await client.post("/users/register", json={"username": "test_user", 
                                                          "email": "test@example.com", 
                                                          "password": "test_password"})
    create_data = create.json()

    login = await client.post("/users/login", json={"email": create_data["email"],
                                                    "password": "test_password"})
    login_data = login.json()
    assert "access_token" in login_data
    assert isinstance(login_data["access_token"], str)
    assert len(login_data["access_token"]) > 0
    assert login.status_code == 200

@pytest.mark.anyio
async def test_login_with_both(client):
    create = await client.post("/users/register", json={"username": "test_user", 
                                                          "email": "test@example.com", 
                                                          "password": "test_password"})
    create_data = create.json()

    login = await client.post("/users/login", json={"username": create_data["username"],
                                                    "email": create_data["email"],
                                                    "password": "test_password"})
    login_data = login.json()
    assert "access_token" in login_data
    assert isinstance(login_data["access_token"], str)
    assert len(login_data["access_token"]) > 0
    assert login.status_code == 200

@pytest.mark.anyio
async def test_login_without_identifier(client):
    create = await client.post("/users/register", json={"username": "test_user", 
                                                          "email": "test@example.com", 
                                                          "password": "test_password"})

    login = await client.post("/users/login", json={"username": "",
                                                    "email": "",
                                                    "password": "test_password"})
    assert "access_token" not in login.json()
    assert login.status_code == 422

@pytest.mark.anyio
async def test_login_wrong_password(client):
    create = await client.post("/users/register", json={"username": "test_user", 
                                                          "email": "test@example.com", 
                                                          "password": "test_password"})
    create_data = create.json()

    login = await client.post("/users/login", json={"username": create_data["username"],
                                                    "email": create_data["email"],
                                                    "password": "wrong_test_password"})
    assert login.status_code == 401

@pytest.mark.anyio
async def test_login_nonexistent_user(client):
    login = await client.post("/users/login", json={"username": "username",
                                                    "password": "test_password"})
    assert login.status_code == 401

# Сценарии получения профиля пользователя

@pytest.mark.anyio
async def test_get_user_profile_authenticated(client):
    create = await client.post("/users/register", json={"username": "test_user", 
                                                          "email": "test@example.com", 
                                                          "password": "test_password"})
    create_data = create.json()

    login = await client.post("/users/login", json={"username": create_data["username"],
                                                    "password": "test_password"})
    login_data = login.json()

    profile = await client.get("/users/profile", 
                               headers={"Authorization": f"Bearer {login_data['access_token']}"})
    profile_data = profile.json()

    assert profile.status_code == 200
    assert profile_data["username"] == "test_user"
    assert profile_data["email"] == "test@example.com"

@pytest.mark.anyio
async def test_get_user_profile_unauthenticated(client):
    profile = await client.get("/users/profile", 
                               headers={"Authorization": f"Bearer"})

    assert profile.status_code == 401
